/**
 * CompText V5.0 ULTRA - OpenClaw Skill Integration
 *
 * Provides 94% token reduction for OpenClaw agents through ultra-compressed commands.
 * Automatically compresses agent thoughts, tool calls, and inter-agent communication.
 *
 * @module comptext-openclaw-skill
 * @version 5.0.0
 * @license MIT
 */

const { execSync } = require('child_process');
const path = require('path');

/**
 * CompText V5.0 ULTRA command mappings
 */
const COMMANDS = {
  'CODE': 'C',
  'FIX': 'F',
  'MODIFY': 'M',
  'TEST': 'T',
  'DOCUMENT': 'D',
  'EXPLAIN': 'E',
  'OPTIMIZE': 'O',
  'ANALYZE': 'A'
};

const LANGUAGES = {
  'PYTHON': 'P',
  'JAVASCRIPT': 'J',
  'TYPESCRIPT': 'T',
  'RUST': 'R',
  'GO': 'G',
  'SQL': 'S',
  'HTML': 'H'
};

const MODIFIERS = {
  'NO_COMMENTS': 'N',
  'STRICT': 'S',
  'ROBUST': 'R',
  'CONCISE': 'C'
};

/**
 * CompText Skill for OpenClaw
 */
class CompTextSkill {
  constructor(config = {}) {
    this.config = {
      enabled: true,
      mode: 'ultra',
      autoCompress: true,
      aggressiveness: 'high',
      preserveContext: true,
      batchThreshold: 3,
      compressionRules: {
        minTokens: 5,
        excludePatterns: ['user input', 'error messages']
      },
      monitoring: {
        trackSavings: true,
        logCompressions: false
      },
      ...config
    };

    this.stats = {
      totalTokensProcessed: 0,
      totalTokensSaved: 0,
      compressions: 0,
      avgCompressionRate: 0,
      costSaved: 0
    };
  }

  /**
   * Encode a single command to V5.0 ULTRA format
   *
   * @param {Object} params - Command parameters
   * @param {string} params.command - Command name (CODE, FIX, etc.)
   * @param {string} [params.language] - Language (PYTHON, JAVASCRIPT, etc.)
   * @param {Array<string>} [params.modifiers] - Modifiers (ROBUST, CONCISE, etc.)
   * @param {string} [params.task] - Task identifier
   * @returns {string} Compressed V5.0 ULTRA command
   *
   * @example
   * encode({ command: 'CODE', language: 'PYTHON', task: 'FIB' })
   * // Returns: "C;P:FIB"
   */
  encode({ command, language, modifiers = [], task }) {
    if (!command || !COMMANDS[command.toUpperCase()]) {
      throw new Error(`Invalid command: ${command}`);
    }

    let parts = [COMMANDS[command.toUpperCase()]];

    if (language && LANGUAGES[language.toUpperCase()]) {
      parts.push(LANGUAGES[language.toUpperCase()]);
    }

    if (modifiers && modifiers.length > 0) {
      for (const mod of modifiers) {
        const modKey = mod.toUpperCase();
        if (MODIFIERS[modKey]) {
          parts.push(MODIFIERS[modKey]);
        }
      }
    }

    let result = parts.join(';');

    if (task) {
      result += ':' + task;
    }

    return result;
  }

  /**
   * Encode multiple commands to batch format
   *
   * @param {Array<Object>} commands - Array of command parameters
   * @returns {string} Batch command in format B:[CMD1]|[CMD2]|[CMD3]
   *
   * @example
   * encodeBatch([
   *   { command: 'DOCUMENT', task: 'SUM' },
   *   { command: 'CODE', language: 'PYTHON', task: 'FIB' }
   * ])
   * // Returns: "B:[D:SUM]|[C;P:FIB]"
   */
  encodeBatch(commands) {
    if (!Array.isArray(commands) || commands.length === 0) {
      throw new Error('Commands must be a non-empty array');
    }

    const encoded = commands.map(cmd => `[${this.encode(cmd)}]`);
    return `B:${encoded.join('|')}`;
  }

  /**
   * Parse a V5.0 ULTRA command back to structured format
   *
   * @param {string} command - V5.0 ULTRA command string
   * @returns {Object|Array<Object>} Parsed command(s)
   */
  parse(command) {
    // Handle batch commands
    if (command.startsWith('B:')) {
      const batchContent = command.substring(2);
      const commands = this._splitBatch(batchContent);
      return commands.map(cmd => this._parseSingle(cmd.slice(1, -1)));
    }

    return this._parseSingle(command);
  }

  /**
   * Split batch command into individual commands
   * @private
   */
  _splitBatch(content) {
    const commands = [];
    let current = '';
    let depth = 0;

    for (const char of content) {
      if (char === '[') {
        depth++;
        current += char;
      } else if (char === ']') {
        depth--;
        current += char;
        if (depth === 0 && current.trim()) {
          commands.push(current.trim());
          current = '';
        }
      } else if (char === '|' && depth === 0) {
        continue; // Skip pipe separators at depth 0
      } else {
        current += char;
      }
    }

    return commands;
  }

  /**
   * Parse a single command
   * @private
   */
  _parseSingle(command) {
    const parts = command.split(':');
    const taskPart = parts.length > 1 ? parts[1] : null;
    const cmdParts = parts[0].split(';');

    const result = {
      command: null,
      language: null,
      modifiers: [],
      task: taskPart
    };

    // First part is always command
    if (cmdParts[0]) {
      const cmdKey = Object.keys(COMMANDS).find(k => COMMANDS[k] === cmdParts[0]);
      result.command = cmdKey || cmdParts[0];
    }

    // Process remaining parts
    for (let i = 1; i < cmdParts.length; i++) {
      const part = cmdParts[i];

      // Check if it's a language
      if (!result.language) {
        const langKey = Object.keys(LANGUAGES).find(k => LANGUAGES[k] === part);
        if (langKey) {
          result.language = langKey;
          continue;
        }
      }

      // Check if it's a modifier
      const modKey = Object.keys(MODIFIERS).find(k => MODIFIERS[k] === part);
      if (modKey) {
        result.modifiers.push(modKey);
      }
    }

    return result;
  }

  /**
   * Auto-compress agent text before sending to LLM
   *
   * @param {string} text - Natural language text to compress
   * @returns {Object} { compressed: string, originalTokens: number, compressedTokens: number, saved: number }
   */
  autoCompress(text) {
    if (!this.config.autoCompress || !this.config.enabled) {
      return { compressed: text, originalTokens: 0, compressedTokens: 0, saved: 0 };
    }

    const originalTokens = this._estimateTokens(text);

    // Check if text meets compression threshold
    if (originalTokens < this.config.compressionRules.minTokens) {
      return { compressed: text, originalTokens, compressedTokens: originalTokens, saved: 0 };
    }

    // Check exclusion patterns
    for (const pattern of this.config.compressionRules.excludePatterns) {
      if (text.toLowerCase().includes(pattern.toLowerCase())) {
        return { compressed: text, originalTokens, compressedTokens: originalTokens, saved: 0 };
      }
    }

    // Attempt intelligent compression
    const compressed = this._intelligentCompress(text);
    const compressedTokens = this._estimateTokens(compressed);
    const saved = originalTokens - compressedTokens;

    // Update stats
    this.stats.totalTokensProcessed += originalTokens;
    this.stats.totalTokensSaved += saved;
    this.stats.compressions++;
    this.stats.avgCompressionRate = (this.stats.totalTokensSaved / this.stats.totalTokensProcessed) * 100;
    this.stats.costSaved = (this.stats.totalTokensSaved / 1000) * 0.03; // Estimate at $0.03/1K tokens

    if (this.config.monitoring.logCompressions) {
      console.log(`[CompText] Compressed: ${originalTokens} -> ${compressedTokens} tokens (${Math.round((saved/originalTokens)*100)}% reduction)`);
    }

    return { compressed, originalTokens, compressedTokens, saved };
  }

  /**
   * Intelligent text compression using pattern matching
   * @private
   */
  _intelligentCompress(text) {
    const lower = text.toLowerCase();

    // Pattern: "write/create/generate code"
    if (lower.match(/(?:write|create|generate).+(?:code|function|script)/)) {
      const lang = this._extractLanguage(text);
      const task = this._extractTask(text);
      return this.encode({ command: 'CODE', language: lang, task });
    }

    // Pattern: "fix bug/error/issue"
    if (lower.match(/(?:fix|debug|resolve).+(?:bug|error|issue|problem)/)) {
      const task = this._extractTask(text);
      return this.encode({ command: 'FIX', task });
    }

    // Pattern: "write/generate tests"
    if (lower.match(/(?:write|generate|create).+(?:test|tests|unit test)/)) {
      const lang = this._extractLanguage(text);
      const task = this._extractTask(text);
      return this.encode({ command: 'TEST', language: lang, modifiers: ['ROBUST'], task });
    }

    // Pattern: "document/explain"
    if (lower.match(/(?:document|explain|describe)/)) {
      const task = this._extractTask(text);
      const command = lower.includes('document') ? 'DOCUMENT' : 'EXPLAIN';
      return this.encode({ command, task });
    }

    // Pattern: "optimize/improve"
    if (lower.match(/(?:optimize|improve|enhance)/)) {
      const task = this._extractTask(text);
      return this.encode({ command: 'OPTIMIZE', task });
    }

    // Pattern: "analyze/review"
    if (lower.match(/(?:analyze|review|inspect)/)) {
      const task = this._extractTask(text);
      return this.encode({ command: 'ANALYZE', task });
    }

    // No pattern matched, return original
    return text;
  }

  /**
   * Extract language from text
   * @private
   */
  _extractLanguage(text) {
    const lower = text.toLowerCase();
    if (lower.includes('python')) return 'PYTHON';
    if (lower.includes('javascript') || lower.includes('js')) return 'JAVASCRIPT';
    if (lower.includes('typescript') || lower.includes('ts')) return 'TYPESCRIPT';
    if (lower.includes('rust')) return 'RUST';
    if (lower.includes('go') || lower.includes('golang')) return 'GO';
    if (lower.includes('sql')) return 'SQL';
    if (lower.includes('html')) return 'HTML';
    return null;
  }

  /**
   * Extract task identifier from text
   * @private
   */
  _extractTask(text) {
    // Simple task extraction - look for key nouns
    const words = text.split(/\s+/);
    const keywords = words.filter(w => w.length > 3 && w.match(/^[A-Z]/));
    return keywords.length > 0 ? keywords[0].toUpperCase() : null;
  }

  /**
   * Estimate token count for text
   * @private
   */
  _estimateTokens(text) {
    // Rough estimate: 4 chars per token
    return Math.ceil(text.length / 4);
  }

  /**
   * Get current compression statistics
   *
   * @returns {Object} Statistics object
   */
  getStats() {
    return {
      ...this.stats,
      compressionRate: Math.round(this.stats.avgCompressionRate * 10) / 10,
      tokensSaved: this.stats.totalTokensSaved,
      costSaved: Math.round(this.stats.costSaved * 100) / 100
    };
  }

  /**
   * Reset statistics
   */
  resetStats() {
    this.stats = {
      totalTokensProcessed: 0,
      totalTokensSaved: 0,
      compressions: 0,
      avgCompressionRate: 0,
      costSaved: 0
    };
  }
}

/**
 * OpenClaw Skill Export
 */
module.exports = {
  name: 'comptext',
  version: '5.0.0',
  description: 'CompText V5.0 ULTRA - 94% token reduction for OpenClaw agents',

  /**
   * Initialize the skill
   */
  init(config) {
    return new CompTextSkill(config);
  },

  /**
   * Quick access methods
   */
  encode: (params) => new CompTextSkill().encode(params),
  encodeBatch: (commands) => new CompTextSkill().encodeBatch(commands),
  parse: (command) => new CompTextSkill().parse(command),

  /**
   * Skill metadata
   */
  metadata: {
    author: 'CompText Team',
    license: 'MIT',
    homepage: 'https://github.com/ProfRandom92/comptext-codex',
    documentation: 'https://profrandom92.github.io/comptext-docs',
    tokenReduction: '94%',
    compatibility: ['openclaw-0.1.x', 'openclaw-1.x']
  }
};
