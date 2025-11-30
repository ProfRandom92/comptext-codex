# CompText-Codex Examples

55+ production-ready examples demonstrating CompText-Codex capabilities.

---

## 📚 Table of Contents

1. [Code Analysis & Optimization](#code-analysis--optimization)
2. [ML Pipelines](#ml-pipelines)
3. [Documentation Generation](#documentation-generation)
4. [Data Visualization](#data-visualization)
5. [DevOps & CI/CD](#devops--cicd)
6. [Security & Compliance](#security--compliance)
7. [Frontend Development](#frontend-development)
8. [ETL Pipelines](#etl-pipelines)
9. [Multi-Agent Systems](#multi-agent-systems)

---

## Code Analysis & Optimization

### Example 1: Performance Bottleneck Detection

```python
from comptext import CompTextParser

parser = CompTextParser()

code = \"\"\"
def process_data(items):
    result = []
    for item in items:
        for other in items:
            if item != other:
                result.append(item + other)
    return result
\"\"\"

command = "@CODE_ANALYZE[perf_bottleneck, complexity] + @CODE_OPT[explain=detail]"
result = parser.execute(command, code=code)
print(result)
```

**Output:**
```
Performance Issues:
- Nested loops: O(n²) time complexity
- List append in loop: inefficient memory usage

Optimized Code:
\"\"\"python
def process_data(items):
    return [item + other for item in items for other in items if item != other]
\"\"\"

Improvement: ~3x faster, O(n²) but more efficient implementation
```

### Example 2: Security Vulnerability Scan

```python
command = "@SEC_SCAN[type=code, severity=high, fix=suggest]"

vulnerable_code = \"\"\"
import pickle
import os

def load_data(filename):
    with open(filename, 'rb') as f:
        return pickle.load(f)

password = os.getenv('PASSWORD')
query = f"SELECT * FROM users WHERE name = '{user_input}'"
\"\"\"

result = parser.execute(command, code=vulnerable_code)
```

**Output:**
```
CRITICAL VULNERABILITIES FOUND:
1. Insecure Deserialization (Line 6)
   - Risk: Remote Code Execution
   - Fix: Use json.load() instead of pickle.load()

2. SQL Injection (Line 10)
   - Risk: Database Compromise
   - Fix: Use parameterized queries

3. Hardcoded Credential (Line 9)
   - Risk: Credential Exposure
   - Fix: Use secure secret management
```

### Example 3: Code Refactoring

```python
command = "@REFACTOR[pattern=solid, tests=generate, docs=update]"

legacy_code = \"\"\"
class UserManager:
    def create_user(self, name, email, role):
        # validation
        if not name or not email:
            return False
        # database
        db.insert('users', {'name': name, 'email': email})
        # email notification
        send_email(email, 'Welcome!')
        # logging
        log.info(f'User {name} created')
        return True
\"\"\"

result = parser.execute(command, code=legacy_code)
```

---

## ML Pipelines

### Example 4: AutoML Classification

```python
command = \"\"\"
@AUTOML[
  task=classification,
  metric=f1,
  cv=5,
  models=[rf, xgb, lgbm],
  optimize=hyperparams
] + @MODEL_EVAL[
  plots=[confusion_matrix, roc_curve, feature_importance],
  export=true
]
\"\"\"

result = parser.execute(command, dataset='customer_churn.csv', target='churned')
```

**Output:**
```
AutoML Pipeline Results:
- Best Model: XGBoost
- F1 Score: 0.87 (CV: 0.85 ± 0.02)
- Hyperparameters: {'max_depth': 7, 'learning_rate': 0.05, 'n_estimators': 200}
- Feature Importance: tenure (0.32), monthly_charges (0.24), contract_type (0.18)
- Model saved to: models/xgb_customer_churn_v1.pkl
- Evaluation plots saved to: reports/evaluation/
```

### Example 5: Feature Engineering

```python
command = "@FEATURE_ENG[auto=true, interactions=2, polynomials=2] + @FEATURE_SELECT[method=recursive, n=20]"

data = pd.read_csv('sales_data.csv')
result = parser.execute(command, dataset=data, target='revenue')
```

---

## Documentation Generation

### Example 6: API Documentation

```python
command = "@DOC_GEN[type=api, format=openapi, examples=true, auth_schemes=true]"

api_code = \"\"\"
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class Item(BaseModel):
    name: str
    price: float
    description: str = None

@app.post("/items/")
async def create_item(item: Item):
    \"\"\"Create a new item in the inventory.\"\"\"
    return {"item_id": 1, "item": item}

@app.get("/items/{item_id}")
async def read_item(item_id: int):
    \"\"\"Retrieve item details by ID.\"\"\"
    if item_id not in database:
        raise HTTPException(status_code=404, detail="Item not found")
    return database[item_id]
\"\"\"

result = parser.execute(command, code=api_code)
```

**Generates complete OpenAPI spec with examples, schemas, and authentication details.**

### Example 7: Changelog Generation

```python
command = "@CHANGELOG[format=markdown, since=v3.0.0, categorize=true, breaking_changes=highlight]"

git_commits = get_commits_since('v3.0.0')
result = parser.execute(command, commits=git_commits)
```

---

## Data Visualization

### Example 8: Interactive Dashboard

```python
command = \"\"\"
@DASHBOARD[
  layout=grid,
  theme=professional,
  responsive=true,
  framework=react,
  charts=[timeseries, bar, pie, heatmap],
  filters=true,
  export=[png, pdf, csv]
]
\"\"\"

data = {
    'sales': sales_df,
    'customers': customers_df,
    'products': products_df
}

result = parser.execute(command, data=data)
# Generates complete React dashboard with Tailwind CSS
```

### Example 9: Statistical Report

```python
command = "@CHART[type=statistical_report, include=[summary_stats, distributions, correlations, outliers]]"

result = parser.execute(command, dataset='financial_data.csv')
```

---

## DevOps & CI/CD

### Example 10: Kubernetes Deployment

```python
command = \"\"\"
@DEPLOY[
  platform=k8s,
  replicas=3,
  autoscaling=true,
  resources=[cpu=500m, mem=1Gi],
  health_check=true,
  monitoring=prometheus,
  logging=elasticsearch
] + @CI_CD[
  stages=[build, test, scan, deploy],
  triggers=[push_main, pull_request],
  notifications=[slack, email]
]
\"\"\"

app_config = {
    'name': 'comptext-api',
    'image': 'comptext-api:latest',
    'port': 8000
}

result = parser.execute(command, config=app_config)
# Generates complete K8s manifests + GitHub Actions workflow
```

---

## Security & Compliance

### Example 11: GDPR Compliance Check

```python
command = "@GDPR[audit=full, generate_report=true, remediation=suggest]"

codebase_path = '/path/to/project'
result = parser.execute(command, path=codebase_path)
```

**Output:**
```
GDPR Compliance Report:
✅ Data Minimization: Compliant
❌ Consent Management: Missing explicit consent forms
❌ Data Encryption: PII fields not encrypted at rest
⚠️  Right to Deletion: Partially implemented (missing cascading deletes)
✅ Privacy Policy: Present and accessible

Remediation Steps:
1. Implement consent management system
2. Encrypt PII fields using AES-256
3. Update deletion logic to cascade across tables
```

---

## Frontend Development

### Example 12: React Component Generation

```python
command = \"\"\"
@COMPONENT[
  framework=react,
  styling=tailwind,
  typescript=true,
  props_validation=true,
  tests=jest,
  storybook=true,
  accessibility=wcag_aa
]
\"\"\"

spec = {
    'name': 'UserCard',
    'props': ['name', 'email', 'avatar', 'role'],
    'actions': ['onEdit', 'onDelete'],
    'variants': ['default', 'compact', 'detailed']
}

result = parser.execute(command, spec=spec)
```

**Generates:**
- `UserCard.tsx` - Component implementation
- `UserCard.test.tsx` - Jest unit tests
- `UserCard.stories.tsx` - Storybook stories
- `UserCard.css` - Tailwind utilities

---

## ETL Pipelines

### Example 13: Data Pipeline

```python
command = \"\"\"
@EXTRACT[source=postgres, query=custom] 
+ @TRANSFORM[
    clean=[nulls, duplicates, outliers],
    normalize=true,
    aggregate=daily,
    enrich=[geo_data, demographics]
] 
+ @LOAD[
    destination=snowflake,
    mode=upsert,
    partition=date,
    validate=schema
]
+ @MONITOR[alerts=true, metrics=[latency, errors, throughput]]
\"\"\"

config = {
    'source_db': 'postgresql://prod-db',
    'target_db': 'snowflake://warehouse',
    'schedule': '0 2 * * *'  # Daily at 2 AM
}

result = parser.execute(command, config=config)
```

---

## Multi-Agent Systems

### Example 14: Agent Orchestration

```python
command = \"\"\"
@AGENT_ROLE[
  name=DataAnalyst,
  capabilities=[sql, python, visualization],
  constraints=[read_only, pii_safe]
] 
+ @AGENT_ROLE[
  name=Copywriter,
  capabilities=[writing, seo, translation],
  constraints=[brand_voice, fact_check]
]
+ @TASK_ASSIGN[
  task=generate_report,
  workflow=[DataAnalyst.analyze, Copywriter.summarize],
  collaboration=sequential
]
\"\"\"

task = {
    'data_source': 'sales_q4.csv',
    'output_format': 'executive_summary',
    'audience': 'C-level'
}

result = parser.execute(command, task=task)
```

---

## More Examples

Visit the `/examples` directory for:
- Web scraping workflows
- NLP pipelines
- Database migrations
- API client generation
- Testing frameworks
- Monitoring dashboards
- And 40+ more!

---

**Want to add your own example? See [CONTRIBUTING.md](CONTRIBUTING.md)!**
