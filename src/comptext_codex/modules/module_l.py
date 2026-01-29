"""Module L: ETL - Data extraction, transformation, loading with validations."""

from typing import Any, Dict, List
from datetime import datetime

from comptext_codex.registry import codex_module, codex_command
from .base import BaseModule


@codex_module(
    code="L",
    name="ETL/Data Pipelines",
    purpose="Data extraction, transformation, loading with validations",
    token_priority="high",
    security={"pii_safe": False, "threat_model": "data_masking"},
    privacy={"dp_budget": "epsilon<=0.5_per_pipeline", "audit_logging": True},
)
class ModuleL(BaseModule):
    """ETL module for data pipelines."""

    @codex_command(syntax="@EXTRACT[source, query, ...]", description="Extract data from various sources", token_cost_hint=70)
    def execute_extract(self, *args, context: Dict[str, Any] = None, **kwargs) -> Dict[str, Any]:
        source = kwargs.get('source', 'database')
        query = kwargs.get('query', None)
        filters = kwargs.get('filters', {})
        batch_size = kwargs.get('batch_size', 1000)
        parallel = kwargs.get('parallel', False)

        # Simulate extraction based on source type
        source_configs = {
            'database': self._extract_database(kwargs),
            'api': self._extract_api(kwargs),
            'file': self._extract_file(kwargs),
            's3': self._extract_s3(kwargs),
            'kafka': self._extract_kafka(kwargs),
            'sftp': self._extract_sftp(kwargs),
            'websocket': self._extract_websocket(kwargs)
        }

        extraction_result = source_configs.get(source, self._extract_database(kwargs))

        return {
            'source': source,
            'source_config': extraction_result,
            'records_extracted': extraction_result.get('record_count', 10000),
            'extraction_time': '2.5s',
            'batches': extraction_result.get('record_count', 10000) // batch_size,
            'batch_size': batch_size,
            'parallel_execution': parallel,
            'filters_applied': filters,
            'status': 'success',
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'schema_detected': True,
                'data_types': self._infer_schema()
            }
        }

    @codex_command(syntax="@TRANSFORM[operations, ...]", description="Transform data with multiple operations", token_cost_hint=65)
    def execute_transform(self, *args, context: Dict[str, Any] = None, **kwargs) -> Dict[str, Any]:
        operations = kwargs.get('operations', [])
        if isinstance(operations, str):
            operations = [operations]

        # Get previous results from context
        input_records = context.get('_last_result', {}).get('records_extracted', 10000) if context else 10000

        # Apply transformations
        transformations = []
        for op in operations:
            if op in ['clean', 'cleanse']:
                transformations.append(self._transform_clean())
            elif op in ['normalize', 'normalise']:
                transformations.append(self._transform_normalize())
            elif op == 'dedupe':
                transformations.append(self._transform_dedupe())
            elif op == 'enrich':
                transformations.append(self._transform_enrich())
            elif op == 'aggregate':
                transformations.append(self._transform_aggregate())
            elif op == 'pivot':
                transformations.append(self._transform_pivot())

        # Additional specific transformations from kwargs
        if kwargs.get('clean'):
            transformations.append(self._transform_clean())
        if kwargs.get('normalize'):
            transformations.append(self._transform_normalize())
        if kwargs.get('type_cast'):
            transformations.append(self._transform_type_cast(kwargs.get('type_cast')))

        valid_records = int(input_records * 0.98)  # 98% pass validation
        filtered_records = input_records - valid_records

        return {
            'transformations_applied': len(transformations),
            'transformation_details': transformations,
            'records_input': input_records,
            'records_processed': input_records,
            'records_valid': valid_records,
            'records_filtered': filtered_records,
            'data_quality_score': 0.98,
            'execution_time': '1.8s',
            'memory_usage': '256MB',
            'status': 'success',
            'warnings': self._generate_warnings(filtered_records)
        }

    @codex_command(syntax="@LOAD[destination, mode, ...]", description="Load data to destination", token_cost_hint=60)
    def execute_load(self, *args, context: Dict[str, Any] = None, **kwargs) -> Dict[str, Any]:
        destination = kwargs.get('destination', 'warehouse')
        mode = kwargs.get('mode', 'append')
        batch_size = kwargs.get('batch_size', 1000)
        verify = kwargs.get('verify', True)

        # Get records from context
        input_records = context.get('_last_result', {}).get('records_valid', 9800) if context else 9800

        destination_configs = {
            'warehouse': self._load_warehouse(kwargs),
            'database': self._load_database(kwargs),
            's3': self._load_s3(kwargs),
            'lake': self._load_data_lake(kwargs),
            'api': self._load_api(kwargs),
            'file': self._load_file(kwargs)
        }

        load_result = destination_configs.get(destination, self._load_warehouse(kwargs))

        return {
            'destination': destination,
            'destination_config': load_result,
            'mode': mode,
            'records_loaded': input_records,
            'records_failed': 0,
            'batch_size': batch_size,
            'batches_completed': input_records // batch_size,
            'load_time': '3.2s',
            'verification': 'passed' if verify else 'skipped',
            'indexes_updated': kwargs.get('update_indexes', True),
            'status': 'success',
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'load_id': 'load_' + datetime.now().strftime('%Y%m%d_%H%M%S'),
                'checksum': 'abc123def456'
            }
        }

    @codex_command(syntax="@VALIDATE[rules, ...]", description="Validate data against rules", token_cost_hint=50)
    def execute_validate(self, *args, context: Dict[str, Any] = None, **kwargs) -> Dict[str, Any]:
        rules = kwargs.get('rules', [])
        strict = kwargs.get('strict', False)

        validation_results = []
        for rule in rules if isinstance(rules, list) else [rules]:
            validation_results.append(self._validate_rule(rule, strict))

        input_records = context.get('_last_result', {}).get('records_processed', 10000) if context else 10000
        failed = sum(v.get('failures', 0) for v in validation_results)

        return {
            'validations_performed': len(validation_results),
            'validation_details': validation_results,
            'records_validated': input_records,
            'records_passed': input_records - failed,
            'records_failed': failed,
            'success_rate': (input_records - failed) / input_records if input_records > 0 else 0,
            'strict_mode': strict,
            'status': 'success' if failed == 0 or not strict else 'warning'
        }

    @codex_command(syntax="@DEDUPE[strategy, keys, ...]", description="Remove duplicate records", token_cost_hint=45)
    def execute_dedupe(self, *args, context: Dict[str, Any] = None, **kwargs) -> Dict[str, Any]:
        strategy = kwargs.get('strategy', 'exact')
        keys = kwargs.get('keys', [])

        input_records = context.get('_last_result', {}).get('records_processed', 10000) if context else 10000
        duplicates_found = int(input_records * 0.05)  # 5% duplicates

        strategies = {
            'exact': 'Exact match on all fields',
            'fuzzy': 'Fuzzy matching with threshold',
            'key_based': f'Based on keys: {", ".join(keys) if keys else "id"}',
            'hash': 'Hash-based deduplication'
        }

        return {
            'strategy': strategy,
            'strategy_description': strategies.get(strategy, strategies['exact']),
            'keys': keys if keys else ['id'],
            'records_input': input_records,
            'duplicates_found': duplicates_found,
            'records_output': input_records - duplicates_found,
            'deduplication_rate': duplicates_found / input_records if input_records > 0 else 0,
            'execution_time': '0.8s',
            'status': 'success'
        }

    @codex_command(syntax="@ENRICH[sources, fields, ...]", description="Enrich data from external sources", token_cost_hint=55)
    def execute_enrich(self, *args, context: Dict[str, Any] = None, **kwargs) -> Dict[str, Any]:
        sources = kwargs.get('sources', [])
        fields = kwargs.get('fields', [])

        input_records = context.get('_last_result', {}).get('records_processed', 10000) if context else 10000
        enriched = int(input_records * 0.95)  # 95% successfully enriched

        enrichment_details = []
        for source in sources if isinstance(sources, list) else [sources]:
            enrichment_details.append({
                'source': source,
                'fields_added': fields if fields else ['additional_field_1', 'additional_field_2'],
                'match_rate': 0.95,
                'api_calls': enriched
            })

        return {
            'enrichment_sources': len(enrichment_details),
            'enrichment_details': enrichment_details,
            'records_input': input_records,
            'records_enriched': enriched,
            'records_not_enriched': input_records - enriched,
            'fields_added': len(fields) if fields else 2,
            'enrichment_rate': enriched / input_records if input_records > 0 else 0,
            'execution_time': '5.2s',
            'status': 'success'
        }

    @codex_command(syntax="@AGGREGATE[operations, group_by, ...]", description="Aggregate data with grouping", token_cost_hint=50)
    def execute_aggregate(self, *args, context: Dict[str, Any] = None, **kwargs) -> Dict[str, Any]:
        operations = kwargs.get('operations', ['sum', 'count'])
        group_by = kwargs.get('group_by', [])

        input_records = context.get('_last_result', {}).get('records_processed', 10000) if context else 10000
        output_groups = len(group_by) * 100 if group_by else 50

        aggregations = []
        for op in operations if isinstance(operations, list) else [operations]:
            aggregations.append({
                'operation': op,
                'field': kwargs.get('field', 'value'),
                'result': f'{op}_result'
            })

        return {
            'aggregations_performed': len(aggregations),
            'aggregation_details': aggregations,
            'group_by_fields': group_by if group_by else ['category'],
            'records_input': input_records,
            'groups_output': output_groups,
            'reduction_ratio': input_records / output_groups if output_groups > 0 else 0,
            'execution_time': '1.2s',
            'status': 'success'
        }

    @codex_command(syntax="@PIPELINE[steps, schedule, ...]", description="Define and execute a complete ETL pipeline", token_cost_hint=75)
    def execute_pipeline(self, *args, context: Dict[str, Any] = None, **kwargs) -> Dict[str, Any]:
        steps = kwargs.get('steps', ['extract', 'transform', 'load'])
        schedule = kwargs.get('schedule', None)
        retry_policy = kwargs.get('retry', {'max_attempts': 3, 'backoff': 'exponential'})

        pipeline_steps = []
        total_time = 0.0

        for step in steps if isinstance(steps, list) else [steps]:
            step_result = {
                'step': step,
                'status': 'success',
                'duration': f'{1.5 + len(step) * 0.1:.1f}s',
                'records_processed': 10000
            }
            total_time += float(step_result['duration'].rstrip('s'))
            pipeline_steps.append(step_result)

        return {
            'pipeline_name': kwargs.get('name', 'etl_pipeline'),
            'steps': len(pipeline_steps),
            'step_details': pipeline_steps,
            'total_execution_time': f'{total_time:.1f}s',
            'schedule': schedule or 'manual',
            'retry_policy': retry_policy,
            'parallel_execution': kwargs.get('parallel', False),
            'status': 'success',
            'next_run': 'Not scheduled' if not schedule else 'In 24 hours',
            'metadata': {
                'pipeline_id': 'pipe_' + datetime.now().strftime('%Y%m%d_%H%M%S'),
                'version': kwargs.get('version', '1.0.0'),
                'author': kwargs.get('author', 'comptext')
            }
        }

    # Helper methods for extraction

    def _extract_database(self, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Extract from database."""
        return {
            'type': 'database',
            'connection': kwargs.get('connection', 'postgres://localhost/db'),
            'table': kwargs.get('table', 'users'),
            'query': kwargs.get('query', 'SELECT * FROM users'),
            'record_count': 10000,
            'columns': ['id', 'name', 'email', 'created_at']
        }

    def _extract_api(self, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Extract from API."""
        return {
            'type': 'api',
            'endpoint': kwargs.get('endpoint', '/api/v1/data'),
            'method': kwargs.get('method', 'GET'),
            'auth': kwargs.get('auth', 'bearer_token'),
            'pagination': kwargs.get('pagination', {'type': 'offset', 'page_size': 100}),
            'record_count': 10000,
            'rate_limit': '1000 req/hour'
        }

    def _extract_file(self, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Extract from file."""
        return {
            'type': 'file',
            'path': kwargs.get('path', '/data/input.csv'),
            'format': kwargs.get('format', 'csv'),
            'delimiter': kwargs.get('delimiter', ','),
            'encoding': kwargs.get('encoding', 'utf-8'),
            'record_count': 10000,
            'file_size': '5.2 MB'
        }

    def _extract_s3(self, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Extract from S3."""
        return {
            'type': 's3',
            'bucket': kwargs.get('bucket', 'data-bucket'),
            'prefix': kwargs.get('prefix', 'raw/'),
            'format': kwargs.get('format', 'parquet'),
            'compression': kwargs.get('compression', 'snappy'),
            'record_count': 10000,
            'objects': 5
        }

    def _extract_kafka(self, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Extract from Kafka."""
        return {
            'type': 'kafka',
            'topic': kwargs.get('topic', 'events'),
            'consumer_group': kwargs.get('consumer_group', 'etl-group'),
            'offset': kwargs.get('offset', 'latest'),
            'record_count': 10000,
            'lag': '0'
        }

    def _extract_sftp(self, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Extract from SFTP."""
        return {
            'type': 'sftp',
            'host': kwargs.get('host', 'sftp.example.com'),
            'path': kwargs.get('path', '/data/'),
            'pattern': kwargs.get('pattern', '*.csv'),
            'record_count': 10000,
            'files': 3
        }

    def _extract_websocket(self, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Extract from WebSocket."""
        return {
            'type': 'websocket',
            'url': kwargs.get('url', 'wss://stream.example.com'),
            'protocol': kwargs.get('protocol', 'json'),
            'record_count': 10000,
            'duration': '60s'
        }

    # Helper methods for transformation

    def _transform_clean(self) -> Dict[str, Any]:
        """Clean data transformation."""
        return {
            'type': 'clean',
            'operations': ['trim_whitespace', 'remove_nulls', 'standardize_case'],
            'records_affected': 1200
        }

    def _transform_normalize(self) -> Dict[str, Any]:
        """Normalize data transformation."""
        return {
            'type': 'normalize',
            'operations': ['scale_values', 'standardize_dates', 'format_phone_numbers'],
            'records_affected': 10000
        }

    def _transform_dedupe(self) -> Dict[str, Any]:
        """Dedupe transformation."""
        return {
            'type': 'dedupe',
            'duplicates_removed': 500,
            'strategy': 'key_based'
        }

    def _transform_enrich(self) -> Dict[str, Any]:
        """Enrich transformation."""
        return {
            'type': 'enrich',
            'fields_added': ['geo_location', 'timezone'],
            'records_enriched': 9500
        }

    def _transform_aggregate(self) -> Dict[str, Any]:
        """Aggregate transformation."""
        return {
            'type': 'aggregate',
            'aggregations': ['sum', 'avg', 'count'],
            'groups': 50
        }

    def _transform_pivot(self) -> Dict[str, Any]:
        """Pivot transformation."""
        return {
            'type': 'pivot',
            'pivot_column': 'category',
            'value_column': 'amount',
            'columns_created': 12
        }

    def _transform_type_cast(self, types: Dict[str, str]) -> Dict[str, Any]:
        """Type casting transformation."""
        return {
            'type': 'type_cast',
            'conversions': types,
            'records_affected': 10000
        }

    # Helper methods for loading

    def _load_warehouse(self, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Load to data warehouse."""
        return {
            'type': 'warehouse',
            'platform': kwargs.get('platform', 'snowflake'),
            'schema': kwargs.get('schema', 'public'),
            'table': kwargs.get('table', 'fact_table'),
            'partitioning': kwargs.get('partition_by', 'date')
        }

    def _load_database(self, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Load to database."""
        return {
            'type': 'database',
            'connection': kwargs.get('connection', 'postgres://localhost/db'),
            'table': kwargs.get('table', 'processed_data'),
            'indexes': kwargs.get('indexes', ['id', 'created_at'])
        }

    def _load_s3(self, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Load to S3."""
        return {
            'type': 's3',
            'bucket': kwargs.get('bucket', 'processed-data'),
            'prefix': kwargs.get('prefix', 'processed/'),
            'format': kwargs.get('format', 'parquet'),
            'compression': kwargs.get('compression', 'snappy')
        }

    def _load_data_lake(self, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Load to data lake."""
        return {
            'type': 'data_lake',
            'platform': kwargs.get('platform', 'delta_lake'),
            'path': kwargs.get('path', '/lake/processed/'),
            'format': kwargs.get('format', 'delta'),
            'partition_by': kwargs.get('partition_by', ['year', 'month'])
        }

    def _load_api(self, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Load via API."""
        return {
            'type': 'api',
            'endpoint': kwargs.get('endpoint', '/api/v1/load'),
            'method': 'POST',
            'batch_size': kwargs.get('batch_size', 100),
            'retry_on_failure': True
        }

    def _load_file(self, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Load to file."""
        return {
            'type': 'file',
            'path': kwargs.get('path', '/data/output.csv'),
            'format': kwargs.get('format', 'csv'),
            'compression': kwargs.get('compression', None)
        }

    # Helper methods for validation

    def _validate_rule(self, rule: str, strict: bool) -> Dict[str, Any]:
        """Validate a single rule."""
        return {
            'rule': rule,
            'type': self._infer_rule_type(rule),
            'records_checked': 10000,
            'failures': 100 if not strict else 0,
            'success_rate': 0.99 if not strict else 1.0
        }

    def _infer_rule_type(self, rule: str) -> str:
        """Infer validation rule type."""
        if 'email' in rule.lower():
            return 'format'
        elif 'not null' in rule.lower() or 'required' in rule.lower():
            return 'presence'
        elif 'range' in rule.lower() or '>' in rule or '<' in rule:
            return 'range'
        elif 'unique' in rule.lower():
            return 'uniqueness'
        return 'custom'

    def _infer_schema(self) -> Dict[str, str]:
        """Infer data schema."""
        return {
            'id': 'integer',
            'name': 'string',
            'email': 'string',
            'created_at': 'timestamp',
            'value': 'float'
        }

    def _generate_warnings(self, filtered_count: int) -> List[str]:
        """Generate warnings based on filtered records."""
        warnings = []
        if filtered_count > 0:
            warnings.append(f'{filtered_count} records filtered due to validation failures')
        if filtered_count > 500:
            warnings.append('High number of filtered records - review data quality')
        return warnings


def get_module() -> ModuleL:
    return ModuleL()
