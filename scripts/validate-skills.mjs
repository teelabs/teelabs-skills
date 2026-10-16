#!/usr/bin/env node

import fs from 'node:fs';
import path from 'node:path';
import process from 'node:process';

const repositoryRoot = process.cwd();
const errors = [];

function fail(message) {
  errors.push(message);
}

function readText(filePath) {
  try {
    return fs.readFileSync(filePath, 'utf8');
  } catch (error) {
    fail(`${path.relative(repositoryRoot, filePath)}: cannot read file (${error.message})`);
    return null;
  }
}

function parseScalar(value, location) {
  const text = value.trim();
  if (text === '') return '';

  if (text.startsWith('"') || text.startsWith("'") || text.endsWith('"') || text.endsWith("'")) {
    if (text.length < 2 || text[0] !== text.at(-1) || !['"', "'"].includes(text[0])) {
      fail(`${location}: malformed quoted value`);
      return text;
    }
    return text.slice(1, -1);
  }

  if (text === 'true') return true;
  if (text === 'false') return false;
  if (text === 'null') return null;
  return text;
}

function parseInlineArray(value, location) {
  if (!value.endsWith(']')) {
    fail(`${location}: malformed array`);
    return [];
  }

  const contents = value.slice(1, -1).trim();
  if (!contents) return [];

  const items = [];
  let current = '';
  let quote = null;
  for (const character of contents) {
    if (quote) {
      current += character;
      if (character === quote) quote = null;
    } else if (character === '"' || character === "'") {
      quote = character;
      current += character;
    } else if (character === ',') {
      if (!current.trim()) fail(`${location}: empty array item`);
      items.push(parseScalar(current, location));
      current = '';
    } else {
      current += character;
    }
  }

  if (quote) fail(`${location}: unterminated quoted array item`);
  if (!current.trim()) fail(`${location}: empty array item`);
  else items.push(parseScalar(current, location));
  return items;
}

function parseFrontmatter(filePath) {
  const relativePath = path.relative(repositoryRoot, filePath);
  const source = readText(filePath);
  if (source === null) return null;

  const lines = source.replace(/^\uFEFF/, '').split(/\r?\n/);
  if (lines[0] !== '---') {
    fail(`${relativePath}: frontmatter must start with ---`);
    return null;
  }

  const end = lines.indexOf('---', 1);
  if (end === -1) {
    fail(`${relativePath}: frontmatter is missing the closing ---`);
    return null;
  }

  const values = {};
  for (let index = 1; index < end; index += 1) {
    const line = lines[index];
    if (!line.trim() || line.trimStart().startsWith('#')) continue;

    const match = /^(\s*)([A-Za-z_][A-Za-z0-9_-]*):(?:[ \t]*(.*))?$/.exec(line);
    if (!match || match[1].length !== 0) {
      fail(`${relativePath}:${index + 1}: malformed top-level frontmatter field`);
      continue;
    }

    const [, , key, rawValue = ''] = match;
    if (Object.hasOwn(values, key)) {
      fail(`${relativePath}:${index + 1}: duplicate frontmatter field ${key}`);
      continue;
    }

    if (/^(?:\|>|\|-|>-)\s*$/.test(rawValue)) {
      const literal = rawValue.startsWith('|');
      const chomping = rawValue.endsWith('-') ? 'strip' : 'keep';
      const block = [];
      index += 1;
      while (index < end) {
        const blockLine = lines[index];
        if (blockLine.trim() && !/^\s+/.test(blockLine)) {
          index -= 1;
          break;
        }
        block.push(blockLine.replace(/^ {2}/, ''));
        index += 1;
      }
      if (index >= end) index = end - 1;

      let blockValue;
      if (literal) {
        blockValue = block.join('\n');
      } else {
        blockValue = block.reduce((result, item, itemIndex) => {
          if (item === '') return itemIndex === block.length - 1 ? result : `${result}\n`;
          return result ? `${result} ${item.trim()}` : item.trim();
        }, '');
      }
      values[key] = chomping === 'keep' ? `${blockValue}\n` : blockValue.replace(/\n+$/, '');
    } else if (rawValue.trim().startsWith('[')) {
      values[key] = parseInlineArray(rawValue.trim(), `${relativePath}:${index + 1}`);
    } else if (rawValue.trim() === '') {
      const items = [];
      let next = index + 1;
      while (next < end && (lines[next].trim() === '' || /^\s+-\s+/.test(lines[next]))) {
        if (lines[next].trim()) items.push(parseScalar(lines[next].replace(/^\s+-\s+/, ''), `${relativePath}:${next + 1}`));
        next += 1;
      }
      if (items.length > 0 || next > index + 1) {
        values[key] = items;
        index = next - 1;
      } else {
        values[key] = '';
      }
    } else {
      values[key] = parseScalar(rawValue, `${relativePath}:${index + 1}`);
    }
  }

  return values;
}

function allMarkdownFiles(directory) {
  const result = [];
  for (const entry of fs.readdirSync(directory, { withFileTypes: true })) {
    const entryPath = path.join(directory, entry.name);
    if (entry.isDirectory()) result.push(...allMarkdownFiles(entryPath));
    else if (entry.isFile() && entry.name.toLowerCase().endsWith('.md')) result.push(entryPath);
  }
  return result;
}

function validateLinks(skillDirectory) {
  for (const markdownPath of allMarkdownFiles(skillDirectory)) {
    const relativePath = path.relative(repositoryRoot, markdownPath);
    const source = readText(markdownPath);
    if (source === null) continue;

    const links = [];
    const inlinePattern = /!?\[[^\]]*\]\(\s*(?:<([^>]+)>|([^\s)]+))/g;
    for (const match of source.matchAll(inlinePattern)) links.push(match[1] ?? match[2]);
    const referencePattern = /^\s*\[[^\]]+\]:\s*(?:<([^>]+)>|(\S+))/gm;
    for (const match of source.matchAll(referencePattern)) links.push(match[1] ?? match[2]);

    for (const target of links) {
      if (/^(?:[a-z][a-z0-9+.-]*:|\/\/)/i.test(target) || target.startsWith('#')) continue;
      const targetPath = decodeURIComponent(target.split(/[?#]/, 1)[0]);
      const resolved = path.resolve(path.dirname(markdownPath), targetPath);
      if (!fs.existsSync(resolved)) {
        fail(`${relativePath}: local link does not resolve: ${target}`);
      }
    }
  }
}

function discoverSkills() {
  const immediateSkills = [];
  for (const entry of fs.readdirSync(repositoryRoot, { withFileTypes: true })) {
    if (entry.isDirectory() && fs.existsSync(path.join(repositoryRoot, entry.name, 'SKILL.md'))) {
      immediateSkills.push({ name: entry.name, directory: path.join(repositoryRoot, entry.name) });
    }
  }

  function findSkillFiles(directory) {
    for (const entry of fs.readdirSync(directory, { withFileTypes: true })) {
      const entryPath = path.join(directory, entry.name);
      if (entry.isDirectory()) {
        if (entry.name === 'SKILL.md') continue;
        findSkillFiles(entryPath);
      } else if (entry.isFile() && entry.name === 'SKILL.md') {
        const relative = path.relative(repositoryRoot, entryPath);
        const parts = relative.split(path.sep);
        if (parts.length === 1) fail(`${relative}: root-level SKILL.md is not allowed`);
        else if (parts.length !== 2 || !immediateSkills.some((skill) => skill.name === parts[0])) {
          fail(`${relative}: nested SKILL.md is not allowed`);
        }
      }
    }
  }
  findSkillFiles(repositoryRoot);
  return immediateSkills;
}

function validateMetadata(skills) {
  const metadataPath = path.join(repositoryRoot, 'skills.json');
  if (!fs.existsSync(metadataPath)) {
    fail('skills.json: file is required');
    return;
  }

  let metadata;
  try {
    metadata = JSON.parse(fs.readFileSync(metadataPath, 'utf8'));
  } catch (error) {
    fail(`skills.json: invalid JSON (${error.message})`);
    return;
  }

  if (!metadata || typeof metadata !== 'object' || Array.isArray(metadata)) {
    fail('skills.json: root value must be an object');
    return;
  }
  if (metadata.schemaVersion !== 1) fail('skills.json: schemaVersion must be 1');
  if (metadata.repository !== 'https://github.com/teelabs/teelabs-skills') {
    fail('skills.json: repository must be https://github.com/teelabs/teelabs-skills');
  }
  if (!Array.isArray(metadata.skills)) {
    fail('skills.json: skills must be an array');
    return;
  }

  const expected = skills.map((skill) => skill.name).sort();
  const listedNames = metadata.skills.map((entry) => entry?.name);
  const actual = [...listedNames].sort();
  if (listedNames.some((name, index) => name !== actual[index])) {
    fail('skills.json: skills must be sorted by name');
  }
  if (actual.length !== expected.length || actual.some((name, index) => name !== expected[index])) {
    fail(`skills.json: skills must contain exactly ${expected.join(', ') || 'no skills'}`);
  }
  for (const [index, entry] of metadata.skills.entries()) {
    if (!entry || typeof entry !== 'object' || Array.isArray(entry)) {
      fail(`skills.json: skills[${index}] must be an object`);
      continue;
    }
    for (const field of ['name', 'path', 'summary']) {
      if (typeof entry[field] !== 'string' || !entry[field].trim()) {
        fail(`skills.json: skills[${index}].${field} must be a non-empty string`);
      }
    }
    if (typeof entry.name === 'string' && typeof entry.path === 'string' && entry.path !== entry.name) {
      fail(`skills.json: skills[${index}].path must match its name`);
    }
  }
}

const skills = discoverSkills();
const names = new Set();
for (const skill of skills) {
  const frontmatter = parseFrontmatter(path.join(skill.directory, 'SKILL.md'));
  if (!frontmatter) continue;
  if (typeof frontmatter.name !== 'string' || !frontmatter.name.trim()) {
    fail(`${skill.name}/SKILL.md: name must be a non-empty string`);
  } else {
    if (!/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(frontmatter.name)) {
      fail(`${skill.name}/SKILL.md: name must be a lowercase hyphenated slug`);
    }
    if (frontmatter.name !== skill.name) fail(`${skill.name}/SKILL.md: name must match the directory name`);
    if (names.has(frontmatter.name)) fail(`${skill.name}/SKILL.md: duplicate skill name ${frontmatter.name}`);
    names.add(frontmatter.name);
  }
  if (typeof frontmatter.description !== 'string' || !frontmatter.description.trim()) {
    fail(`${skill.name}/SKILL.md: description must be a non-empty string`);
  }
  validateLinks(skill.directory);
}
validateMetadata(skills);

if (errors.length > 0) {
  console.error(`Skill validation failed with ${errors.length} error${errors.length === 1 ? '' : 's'}:`);
  for (const error of errors) console.error(`- ${error}`);
  process.exitCode = 1;
} else {
  console.log(`Validated ${skills.length} skill${skills.length === 1 ? '' : 's'}: ${skills.map((skill) => skill.name).join(', ')}`);
}
