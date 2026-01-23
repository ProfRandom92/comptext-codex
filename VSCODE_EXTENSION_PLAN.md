# CompText Codex VS Code Extension - Architecture Plan

## Overview

A VS Code extension that provides comprehensive support for CompText DSL, including syntax highlighting, IntelliSense, command execution, and integrated debugging.

## Features

### 1. Language Support

#### Syntax Highlighting
- **Module codes** (A-M): Highlighted in distinct colors
- **Command names**: Keyword highlighting
- **Parameters**: Argument/parameter syntax
- **Operators**: Chain operator (+), brackets, colons
- **Comments**: Support for line and block comments

#### Grammar Definition (TextMate)
```json
{
  "scopeName": "source.comptext",
  "patterns": [
    {
      "name": "keyword.operator.comptext",
      "match": "@([A-M]):"
    },
    {
      "name": "entity.name.function.comptext",
      "match": "(?<=@[A-M]:)\\w+"
    },
    {
      "name": "keyword.operator.chain.comptext",
      "match": "\\+"
    }
  ]
}
```

### 2. IntelliSense & Autocomplete

#### Features
- **Command completion**: Type `@` to see all available modules
- **Module-specific commands**: After typing `@A:`, show Module A commands
- **Parameter suggestions**: Context-aware parameter completion
- **Documentation on hover**: Show command description and examples

#### Implementation
```typescript
class CompTextCompletionProvider implements vscode.CompletionItemProvider {
  provideCompletionItems(
    document: vscode.TextDocument,
    position: vscode.Position
  ): vscode.CompletionItem[] {
    // Parse context and provide relevant completions
  }
}
```

### 3. Command Execution

#### Execute in Editor
- **Execute current line**: `Ctrl+Enter`
- **Execute selection**: `Ctrl+Shift+Enter`
- **Execute file**: `Ctrl+Shift+P` → "CompText: Execute File"

#### Output Panel
- Dedicated output channel for results
- Formatted JSON/text output
- Error highlighting and stack traces
- Token count statistics

#### Implementation
```typescript
async function executeCompTextCommand(command: string): Promise<void> {
  const terminal = vscode.window.createTerminal('CompText');
  terminal.sendText(`comptext execute "${command}"`);
  terminal.show();
}
```

### 4. REPL Integration

#### Integrated Terminal REPL
- Launch REPL from command palette
- Send selections to REPL
- History navigation
- Clear REPL command

#### Features
- Syntax highlighting in REPL terminal
- Command history (up/down arrows)
- Multi-line input support
- Context preservation

### 5. Code Actions & Refactoring

#### Quick Fixes
- Format command
- Optimize command (suggest shorter version)
- Convert between syntax styles
- Add/remove parameters

#### Code Actions
```typescript
class CompTextCodeActionProvider implements vscode.CodeActionProvider {
  provideCodeActions(
    document: vscode.TextDocument,
    range: vscode.Range
  ): vscode.CodeAction[] {
    return [
      {
        title: "Format CompText Command",
        command: "comptext.formatCommand"
      },
      {
        title: "Show Token Count",
        command: "comptext.showTokenCount"
      }
    ];
  }
}
```

### 6. Diagnostics & Linting

#### Real-time Validation
- Parse errors highlighted inline
- Unknown module/command warnings
- Parameter type checking
- Suggestions for corrections

#### Diagnostic Provider
```typescript
class CompTextDiagnosticProvider {
  provideDiagnostics(document: vscode.TextDocument): vscode.Diagnostic[] {
    const diagnostics: vscode.Diagnostic[] = [];

    // Parse document and validate
    const commands = parseDocument(document);

    for (const cmd of commands) {
      if (!isValidModule(cmd.module)) {
        diagnostics.push(
          new vscode.Diagnostic(
            cmd.range,
            `Unknown module: ${cmd.module}`,
            vscode.DiagnosticSeverity.Error
          )
        );
      }
    }

    return diagnostics;
  }
}
```

### 7. Token Counter

#### Real-time Token Display
- Status bar item showing token count
- Compare with natural language estimate
- Reduction percentage display

#### Status Bar Integration
```typescript
const tokenStatusBar = vscode.window.createStatusBarItem(
  vscode.StatusBarAlignment.Right,
  100
);

function updateTokenCount(document: vscode.TextDocument): void {
  const tokens = calculateTokens(document.getText());
  tokenStatusBar.text = `$(symbol-numeric) ${tokens} tokens`;
  tokenStatusBar.show();
}
```

### 8. Playground View

#### Webview Panel
- Interactive playground within VS Code
- Side-by-side comparison view
- Live token counter
- Example gallery

#### Implementation
```typescript
class PlaygroundPanel {
  public static createOrShow(extensionUri: vscode.Uri) {
    const panel = vscode.window.createWebviewPanel(
      'comptextPlayground',
      'CompText Playground',
      vscode.ViewColumn.One,
      {
        enableScripts: true,
        localResourceRoots: [extensionUri]
      }
    );

    panel.webview.html = getPlaygroundHTML();
  }
}
```

### 9. Snippets

#### Built-in Snippets
- Common command patterns
- ETL pipelines
- UI component generation
- ML workflows

#### Snippet Definitions
```json
{
  "ETL Pipeline": {
    "prefix": "etl",
    "body": [
      "@EXTRACT[source=${1:database}, table=${2:users}] +",
      "@TRANSFORM[operations=['${3:clean}','${4:normalize}']] +",
      "@LOAD[destination=${5:warehouse}, mode=${6:append}]"
    ],
    "description": "Complete ETL pipeline"
  },
  "React Component": {
    "prefix": "react",
    "body": [
      "@COMPONENT[framework=react, typescript=${1:true}, styling=${2:styled-components}]"
    ],
    "description": "React component generation"
  }
}
```

### 10. Module Explorer

#### Tree View
- Browse all modules A-M
- Expand to see commands
- Click to insert command template
- Show documentation inline

#### Tree Data Provider
```typescript
class ModuleTreeDataProvider implements vscode.TreeDataProvider<ModuleItem> {
  getChildren(element?: ModuleItem): ModuleItem[] {
    if (!element) {
      // Return root modules A-M
      return getModules();
    } else {
      // Return commands for this module
      return getCommandsForModule(element.code);
    }
  }
}
```

## Project Structure

```
comptext-vscode/
├── package.json              # Extension manifest
├── tsconfig.json             # TypeScript configuration
├── src/
│   ├── extension.ts         # Extension entry point
│   ├── providers/
│   │   ├── completionProvider.ts
│   │   ├── hoverProvider.ts
│   │   ├── diagnosticProvider.ts
│   │   ├── codeActionProvider.ts
│   │   └── treeDataProvider.ts
│   ├── commands/
│   │   ├── execute.ts
│   │   ├── format.ts
│   │   └── tokenCount.ts
│   ├── parser/
│   │   ├── parser.ts
│   │   └── validator.ts
│   ├── repl/
│   │   └── replManager.ts
│   ├── webview/
│   │   └── playground.ts
│   └── utils/
│       ├── tokenCounter.ts
│       └── modules.ts
├── syntaxes/
│   └── comptext.tmLanguage.json
├── snippets/
│   └── comptext.json
├── media/
│   ├── icons/
│   └── playground/
└── test/
    ├── suite/
    └── fixtures/
```

## Configuration Settings

```json
{
  "comptext.codexPath": {
    "type": "string",
    "default": "./codex",
    "description": "Path to CompText codex directory"
  },
  "comptext.autoFormat": {
    "type": "boolean",
    "default": true,
    "description": "Automatically format commands on save"
  },
  "comptext.showTokenCount": {
    "type": "boolean",
    "default": true,
    "description": "Show token count in status bar"
  },
  "comptext.executionTimeout": {
    "type": "number",
    "default": 30000,
    "description": "Command execution timeout in milliseconds"
  },
  "comptext.enableDiagnostics": {
    "type": "boolean",
    "default": true,
    "description": "Enable real-time diagnostics and validation"
  }
}
```

## Commands

| Command ID | Title | Keybinding |
|-----------|-------|------------|
| `comptext.execute` | Execute CompText Command | `Ctrl+Enter` |
| `comptext.executeSelection` | Execute Selection | `Ctrl+Shift+Enter` |
| `comptext.format` | Format Command | `Shift+Alt+F` |
| `comptext.openRepl` | Open REPL | - |
| `comptext.openPlayground` | Open Playground | - |
| `comptext.showTokenCount` | Show Token Count | - |
| `comptext.insertModule` | Insert Module | - |

## Extension Manifest (package.json)

```json
{
  "name": "comptext-codex",
  "displayName": "CompText Codex",
  "description": "Language support for CompText DSL",
  "version": "1.0.0",
  "publisher": "comptext",
  "engines": {
    "vscode": "^1.80.0"
  },
  "categories": [
    "Programming Languages",
    "Formatters",
    "Linters"
  ],
  "activationEvents": [
    "onLanguage:comptext",
    "onCommand:comptext.execute"
  ],
  "main": "./out/extension.js",
  "contributes": {
    "languages": [
      {
        "id": "comptext",
        "aliases": ["CompText", "comptext"],
        "extensions": [".ct", ".comptext"],
        "configuration": "./language-configuration.json"
      }
    ],
    "grammars": [
      {
        "language": "comptext",
        "scopeName": "source.comptext",
        "path": "./syntaxes/comptext.tmLanguage.json"
      }
    ],
    "snippets": [
      {
        "language": "comptext",
        "path": "./snippets/comptext.json"
      }
    ]
  }
}
```

## Development Roadmap

### Phase 1: Core Language Support (Weeks 1-2)
- [x] Basic syntax highlighting
- [x] Language configuration
- [x] Extension scaffolding
- [ ] TextMate grammar
- [ ] File type association

### Phase 2: IntelliSense & Completion (Weeks 3-4)
- [ ] Completion provider
- [ ] Hover provider
- [ ] Signature help
- [ ] Documentation integration
- [ ] Parameter hints

### Phase 3: Execution & REPL (Weeks 5-6)
- [ ] Command execution
- [ ] Output panel
- [ ] REPL integration
- [ ] Terminal support
- [ ] Error handling

### Phase 4: Advanced Features (Weeks 7-8)
- [ ] Diagnostics and linting
- [ ] Code actions
- [ ] Quick fixes
- [ ] Refactoring support
- [ ] Token counter

### Phase 5: UI Components (Weeks 9-10)
- [ ] Module explorer
- [ ] Playground webview
- [ ] Settings panel
- [ ] Documentation viewer
- [ ] Example browser

### Phase 6: Testing & Polish (Weeks 11-12)
- [ ] Unit tests
- [ ] Integration tests
- [ ] Performance optimization
- [ ] Documentation
- [ ] Marketplace preparation

## Testing Strategy

### Unit Tests
```typescript
import * as assert from 'assert';
import { parseCompTextCommand } from '../parser/parser';

suite('Parser Tests', () => {
  test('Parse simple command', () => {
    const result = parseCompTextCommand('@A:compress text');
    assert.strictEqual(result.module, 'A');
    assert.strictEqual(result.command, 'compress');
  });
});
```

### Integration Tests
- Test with real CompText CLI
- Validate against codex definitions
- Test command execution
- Test error handling

## Deployment

### VS Code Marketplace
1. Package extension: `vsce package`
2. Test .vsix file locally
3. Publish: `vsce publish`
4. Monitor adoption and feedback

### Continuous Integration
- GitHub Actions workflow
- Automated testing on push
- Automated publishing on tag

## Future Enhancements

1. **AI-Powered Suggestions**
   - Suggest optimal commands based on context
   - Auto-complete based on common patterns

2. **Command History**
   - Track frequently used commands
   - Quick access to recent commands

3. **Collaborative Features**
   - Share commands with team
   - Command library sync

4. **Performance Monitoring**
   - Track execution times
   - Visualize token savings

5. **Extension API**
   - Allow other extensions to use CompText
   - Plugin system for custom modules

## Resources

- [VS Code Extension API](https://code.visualstudio.com/api)
- [Language Extension Guide](https://code.visualstudio.com/api/language-extensions/overview)
- [TextMate Grammar](https://macromates.com/manual/en/language_grammars)
- [Extension Samples](https://github.com/microsoft/vscode-extension-samples)

## License

MIT License - See LICENSE file for details

---

**Status**: Planning Complete
**Next Steps**: Begin Phase 1 implementation
**Target Release**: Q2 2026
