# GitHub Copilot Instructions for CompText-Codex

## About CompText

CompText is a Domain-Specific Language (DSL) for efficient LLM interaction. It reduces prompt tokens by 50-80% compared to natural language while maintaining precision and clarity.

**Think of CompText as "SQL for LLMs" - structured, composable commands that replace verbose natural language.**

## Core Vocabulary

When working with CompText, you should understand and recognize these core elements:

### CMD (Command)
The basic unit of CompText - a specific instruction or operation.

**Format:** `@COMMAND[parameters]`

**Examples:**
- `@CODE_ANALYZE[perf_bottleneck]` - Analyze code for performance issues
- `@SUMMARIZE[length=short]` - Summarize text briefly
- `@REFACTOR[pattern=solid]` - Refactor code following SOLID principles

### LNG (Language)
Specifies the programming language or natural language context for an operation.

**Examples:**
- `@CODE_ANALYZE[lang=python]` - Analyze Python code
- `@TRANSLATE[target_lang=german]` - Translate to German
- `@DOC_GEN[lang=typescript]` - Generate TypeScript documentation

### STY (Style)
Defines the stylistic approach or formatting for output.

**Examples:**
- `@FORMAT[style=professional]` - Professional formatting
- `@CODE_OPT[style=readable]` - Optimize for readability
- `@DOC_GEN[style=tutorial]` - Tutorial-style documentation

### SKL (Skill)
Indicates the skill level or complexity target for the output.

**Examples:**
- `@EXPLAIN[skill=beginner]` - Explain for beginners
- `@DOC_GEN[skill=expert]` - Advanced technical documentation
- `@TUTORIAL[skill=intermediate]` - Intermediate-level tutorial

## Module Structure

CompText is organized into 18 production modules (A-R):

| Module | Name | Purpose |
|--------|------|---------|
| **A** | Core Commands | Essential DSL commands for text manipulation |
| **B** | Analysis | Text analysis and insight generation |
| **C** | Formatting | Document formatting and structure |
| **D** | AI Control | Model selection, prompt governance, safety filters |
| **E** | ML Pipelines | AutoML, feature engineering, experiment tracking |
| **F** | Documentation | API docs, tutorials, changelogs, design docs |
| **G** | Testing & Batch Processing | Test generation, coverage insights, batch operations |
| **H** | Database | Schema design, migrations, query optimization |
| **I** | Security | Vulnerability scans, compliance, threat modeling |
| **J** | DevOps | CI/CD workflows, observability, release automation |
| **K** | Frontend/UI | Component scaffolding, accessibility, responsive design |
| **L** | ETL | Data extraction, transformation, loading |
| **M** | MCP Integration | Multi-agent messaging, tool routing |
| **N** | Agent Orchestration | Multi-agent coordination, workflow management |
| **O** | Observability | Metrics collection, distributed tracing |
| **P** | Performance | Caching strategies, optimization hints |
| **Q** | Quality Assurance | Code quality gates, linting, standards |
| **R** | Release Management | Version control, changelog generation |

## Command Syntax

### Basic Commands
```
@COMMAND[param1, param2, key=value]
```

### Chaining Commands
```
@CMD1[...] + @CMD2[...] + @CMD3[...]
```

### Conditional Execution
```
@CMD1[...] IF condition THEN @CMD2[...] ELSE @CMD3[...]
```

### Batch Processing (NEW - Module G)
```
BATCH[mode=SEQ|PAR]: [@CMD1[...]] || [@CMD2[...]] || [@CMD3[...]]
```

**Modes:**
- `SEQ` - Sequential execution (default) - commands run one after another
- `PAR` - Parallel execution - commands run simultaneously

**Examples:**
```
# Sequential data pipeline
BATCH[mode=SEQ]: [@EXTRACT[source=db]] || [@TRANSFORM[clean=true]] || [@LOAD[dest=warehouse]]

# Parallel code analysis
BATCH[mode=PAR]: [@CODE_ANALYZE[file1.py]] || [@CODE_ANALYZE[file2.py]] || [@CODE_ANALYZE[file3.py]]
```

## Example Command Categories

### Code Analysis & Optimization
```
@CODE_ANALYZE[perf_bottleneck, complexity]
@CODE_OPT[explain=detail, bench=compare]
@REFACTOR[pattern=mvc, tests=preserve]
@DEBUG[trace=true, breakpoints=auto]
```

### Documentation Generation
```
@DOC_GEN[api, format=markdown, include_examples=true]
@CHANGELOG[source=git, format=keepachangelog]
@TUTORIAL[topic=quickstart, skill=beginner]
```

### Testing
```
@TEST_GEN[coverage=branch, framework=pytest]
@TEST_RUN[suite=integration, parallel=true]
@QUALITY_CHECK[gates=all, severity=high]
```

### Security & Compliance
```
@SEC_SCAN[type=code, severity=high, fix=suggest]
@COMPLIANCE_CHECK[standard=gdpr, report=detailed]
@THREAT_MODEL[scope=api, mitigations=suggest]
```

### Data Operations
```
@EXTRACT[source=db, query=select_users]
@TRANSFORM[clean=true, validate=schema]
@LOAD[dest=warehouse, mode=append]
```

### ML Pipelines
```
@AUTOML[task=classification, metric=f1]
@FEATURE_ENG[auto=true, methods=[scale, encode]]
@MODEL_EVAL[cv=5, metrics=[accuracy, precision, recall]]
```

## Token Efficiency Guidelines

When working with CompText code:

1. **Recognize CompText Syntax**: If you see `@COMMAND[...]` patterns, you're working with CompText DSL
2. **Preserve Token Efficiency**: Don't expand CompText commands into natural language unnecessarily
3. **Use Batch Operations**: When you see multiple similar commands, consider suggesting batch processing
4. **Maintain Brevity**: CompText is about efficiency - keep it concise

### Example Conversion

**Natural Language (62 tokens):**
> "Please analyze this Python code, identify performance bottlenecks, suggest optimizations with code examples, explain the reasoning behind each optimization, and provide benchmark comparisons showing expected improvements"

**CompText (18 tokens):**
```
@CODE_ANALYZE[perf_bottleneck] + @CODE_OPT[explain=detail, bench=compare]
```

**Result: 71% token reduction**

## Important Rules

### 🎯 Rule #1: Always prioritize brevity over politeness when CompText is active

When CompText DSL is being used:
- **DO**: Be direct, concise, and efficient
- **DO**: Focus on technical accuracy and token efficiency
- **DON'T**: Add unnecessary pleasantries or verbose explanations
- **DON'TNEE**: Use filler words like "please", "thank you", "I think", "perhaps"
- **DON'T**: Apologize for being brief - brevity is the goal

**Example:**

❌ **Verbose (Avoid):**
> "Thank you for sharing that code! I'd be happy to help you analyze it. If you don't mind, I think it would be great if we could look at potential performance issues. Would it be okay if I also suggest some optimizations? I really appreciate your patience!"

✅ **Brief (Preferred):**
> "Analyzing code for performance issues and suggesting optimizations."

OR even better with CompText:
> "@CODE_ANALYZE[perf_bottleneck] + @CODE_OPT[explain=detail]"

### Rule #2: Maintain Precision

While being brief, always maintain technical precision:
- Use exact parameter names
- Follow established CompText syntax
- Preserve module structure and command relationships

### Rule #3: Suggest CompText Where Applicable

When you see verbose natural language prompts that could be converted to CompText:
- Suggest the CompText equivalent
- Show the token savings
- Explain the conversion briefly

### Rule #4: Respect Module Boundaries

Each module has a specific purpose. Don't mix concerns unnecessarily:
- Security operations → Module I
- Testing operations → Module G
- Documentation → Module F
- Keep commands within their appropriate modules

### Rule #5: Batch When Appropriate

If you see multiple independent commands, suggest batch processing:
- Use `PAR` for independent operations
- Use `SEQ` for dependent pipelines
- Show the token efficiency gains

## Error Handling

When encountering CompText errors:
1. Check command syntax: `@COMMAND[params]`
2. Verify parameter format: `key=value` or positional
3. Ensure proper module reference
4. Validate batch syntax if using BATCH commands

## Best Practices

1. **Learn the Pattern**: CompText follows consistent patterns across modules
2. **Think Efficiency**: Every word costs tokens - make them count
3. **Use Composition**: Chain commands with `+` to build complex operations
4. **Leverage Batching**: Group related commands for efficiency
5. **Stay Current**: New modules and commands are added regularly

## Integration with Development Workflow

CompText works alongside:
- **MCP (Model Context Protocol)**: For multi-agent systems
- **CLI tools**: Command-line interface for validation and testing
- **Python API**: Programmatic access to CompText functionality
- **Web Playground**: Interactive DSL editor for learning and testing

## Resources

- **Repository**: https://github.com/ProfRandom92/comptext-codex
- **Module Catalog**: `codex/MODULE_CATALOG.md`
- **Examples**: `EXAMPLES.md` (55+ production examples)
- **Token Reduction Results**: `TOKEN_REDUCTION_RESULTS.md`
- **Quick Start**: `QUICK_START.md`

## Summary

When you encounter CompText in this repository:
1. **Recognize** the DSL syntax and structure
2. **Respect** the token efficiency principles
3. **Maintain** brevity over politeness
4. **Suggest** CompText alternatives for verbose prompts
5. **Use** batch processing for multiple operations
6. **Stay** precise and technically accurate

**Remember: CompText is about maximizing efficiency while maintaining clarity. Be direct, be brief, be precise.**
