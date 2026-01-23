"""Example: Token optimization demonstration.

Compares natural language vs CompText for various tasks
to demonstrate token reduction.
"""

from comptext_codex import token_count, calculate_reduction


def main():
    """Demonstrate token savings across different scenarios."""

    print("=== Token Optimization Examples ===\n")

    scenarios = [
        {
            "name": "Data Pipeline",
            "natural": "Please extract data from the PostgreSQL database table named 'users', then clean and normalize the data by removing null values and standardizing the format, validate that all email addresses are properly formatted and all required fields are present, and finally load the processed data into the data warehouse using append mode with batch size of 1000 records",
            "comptext": "@EXTRACT[source=database, table=users] + @TRANSFORM[operations=['clean','normalize']] + @VALIDATE[rules=['email','not_null']] + @LOAD[destination=warehouse, mode=append, batch_size=1000]"
        },
        {
            "name": "UI Component",
            "natural": "Create a React component using TypeScript with styled-components for styling. The component should be a functional component with local state management. Include accessibility features that meet WCAG AA standards, make it responsive across all breakpoints, and generate test files using Jest.",
            "comptext": "@COMPONENT[framework=react, typescript=true, styling=styled-components, type=functional, state=local, accessibility=wcag_aa, responsive=true, test_framework=jest]"
        },
        {
            "name": "ML Model Training",
            "natural": "Set up an automated machine learning pipeline for classification task, optimize for F1 score as the primary metric, use 5-fold cross-validation for model evaluation, train multiple models including random forest, XGBoost, and LightGBM, perform hyperparameter tuning using Bayesian optimization with 50 trials, and generate a comprehensive evaluation report.",
            "comptext": "@AUTOML[task=classification, metric=f1, cv_folds=5, models=['rf','xgb','lgbm']] + @HYPERPARAM_TUNE[method=bayesian, n_trials=50] + @MODEL_EVALUATE[report=comprehensive]"
        },
        {
            "name": "Security Scan",
            "natural": "Perform a comprehensive security vulnerability scan checking for all OWASP Top 10 vulnerabilities, analyze dependencies for known security issues with medium or higher severity, check GDPR compliance including data processing procedures and consent tracking mechanisms, and generate a detailed security report with remediation recommendations.",
            "comptext": "@SEC_SCAN[owasp_top10=true] + @VULN_SCAN[scan_type=dependencies, severity_threshold=medium] + @GDPR_CHECK[data_processing=true, consent_tracking=true] + @SECURITY_REPORT[include_remediation=true]"
        },
        {
            "name": "CI/CD Pipeline",
            "natural": "Configure a continuous integration and deployment pipeline using GitHub Actions with parallel execution of build, test, and lint stages. Set up deployment to production environment using blue-green deployment strategy with automatic rollback on failure. Configure monitoring with Grafana dashboards tracking CPU usage, memory consumption, and response times with automatic alerts.",
            "comptext": "@CI_CD[platform=github_actions, stages=['build','test','lint'], parallel=true] + @DEPLOY[environment=production, strategy=blue_green, rollback=auto] + @MONITOR[metrics=['cpu','memory','response_time'], alerts=true, dashboard=grafana]"
        }
    ]

    total_natural = 0
    total_comptext = 0

    for scenario in scenarios:
        natural_tokens = token_count(scenario["natural"])
        comptext_tokens = token_count(scenario["comptext"])
        reduction = calculate_reduction(scenario["natural"], scenario["comptext"])

        total_natural += natural_tokens
        total_comptext += comptext_tokens

        print(f"Scenario: {scenario['name']}")
        print(f"  Natural Language: {natural_tokens} tokens")
        print(f"  CompText:         {comptext_tokens} tokens")
        print(f"  Reduction:        {reduction:.1f}%")
        print(f"  Tokens Saved:     {natural_tokens - comptext_tokens}")
        print()

    # Overall statistics
    overall_reduction = ((total_natural - total_comptext) / total_natural) * 100
    print("=" * 50)
    print(f"OVERALL STATISTICS")
    print(f"  Total Natural Language Tokens: {total_natural}")
    print(f"  Total CompText Tokens:         {total_comptext}")
    print(f"  Average Reduction:             {overall_reduction:.1f}%")
    print(f"  Total Tokens Saved:            {total_natural - total_comptext}")
    print("=" * 50)


if __name__ == "__main__":
    main()
