"""Tests for CompText Modules."""

import pytest
from comptext_codex.modules.module_a import ModuleA
from comptext_codex.modules.module_b import ModuleB
from comptext_codex.modules.module_e import ModuleE
from comptext_codex.modules.module_i import ModuleI


class TestModuleA:
    """Test Module A: Core Commands."""

    def test_compress(self):
        """Test text compression."""
        module = ModuleA()
        result = module.execute_compress("The quick brown fox jumps over the lazy dog repeatedly")

        assert isinstance(result, str)
        assert len(result) > 0

    def test_expand(self):
        """Test text expansion."""
        module = ModuleA()
        result = module.execute_expand("QBF")

        assert isinstance(result, str)
        assert "Expanded" in result


class TestModuleB:
    """Test Module B: Analysis."""

    def test_analyze(self):
        """Test text analysis."""
        module = ModuleB()
        result = module.execute_analyze("This is a great positive message with good vibes")

        assert 'word_count' in result
        assert 'sentiment' in result
        assert 'keywords' in result
        assert result['sentiment'] == 'positive'

    def test_code_analyze(self):
        """Test code analysis."""
        module = ModuleB()
        code = "def test(): pass"
        result = module.execute_code_analyze(
            'perf_bottleneck',
            'complexity',
            context={'code': code}
        )

        assert 'code_length' in result
        assert 'line_count' in result
        assert 'issues' in result

    def test_sentiment_analysis(self):
        """Test sentiment detection."""
        module = ModuleB()

        # Positive sentiment
        result_pos = module.execute_analyze("This is excellent and great")
        assert result_pos['sentiment'] == 'positive'

        # Negative sentiment
        result_neg = module.execute_analyze("This is terrible and bad")
        assert result_neg['sentiment'] == 'negative'


class TestModuleE:
    """Test Module E: ML Pipelines."""

    def test_automl(self):
        """Test AutoML execution."""
        module = ModuleE()
        result = module.execute_automl(
            task='classification',
            metric='f1',
            models=['rf', 'xgb']
        )

        assert result['task'] == 'classification'
        assert result['metric'] == 'f1'
        assert 'best_model' in result
        assert 'score' in result

    def test_feature_engineering(self):
        """Test feature engineering."""
        module = ModuleE()
        result = module.execute_feature_eng(auto=True)

        assert 'features_created' in result
        assert 'feature_types' in result


class TestModuleI:
    """Test Module I: Security."""

    def test_security_scan(self):
        """Test security vulnerability scan."""
        module = ModuleI()
        result = module.execute_sec_scan(type='code', severity='high')

        assert result['scan_type'] == 'code'
        assert 'vulnerabilities_found' in result
        assert 'recommendations' in result

    def test_gdpr_audit(self):
        """Test GDPR compliance audit."""
        module = ModuleI()
        result = module.execute_gdpr(audit='full')

        assert result['audit_type'] == 'full'
        assert 'compliant' in result
        assert 'issues' in result
        assert 'recommendations' in result


class TestModuleCommands:
    """Test module command listing."""

    def test_module_commands(self):
        """Test getting commands from modules."""
        modules = [ModuleA(), ModuleB(), ModuleE(), ModuleI()]

        for module in modules:
            commands = module.get_commands()
            assert isinstance(commands, list)
            assert len(commands) > 0
            assert all('module' in cmd for cmd in commands)
            assert all('command' in cmd for cmd in commands)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
