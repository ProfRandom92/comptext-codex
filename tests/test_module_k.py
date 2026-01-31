"""Comprehensive tests for Module K: Frontend/UI."""

import pytest

from comptext_codex.modules.module_k import ModuleK, get_module


@pytest.fixture
def module():
    """Create a ModuleK instance."""
    return ModuleK()


class TestModuleKBasics:
    """Test basic module functionality."""

    def test_get_module(self):
        """Test get_module factory function."""
        mod = get_module()
        assert isinstance(mod, ModuleK)

    def test_module_instance(self, module):
        """Test module is a ModuleK instance."""
        assert isinstance(module, ModuleK)


class TestComponentCommand:
    """Test execute_component command."""

    def test_component_defaults(self, module):
        """Test component with default settings."""
        result = module.execute_component(context={})
        assert result['framework'] == 'react'
        assert result['type'] == 'functional'
        assert result['styling'] == 'css-modules'
        assert result['typescript'] is True
        assert 'Component.tsx' in result['files_generated']
        assert 'Component.test.tsx' in result['files_generated']

    def test_component_javascript(self, module):
        """Test component with JavaScript (no TypeScript)."""
        result = module.execute_component(context={}, typescript=False)
        assert result['typescript'] is False
        assert 'Component.jsx' in result['files_generated']

    def test_component_redux_state(self, module):
        """Test component with Redux state management."""
        result = module.execute_component(context={}, state='redux')
        assert result['state_management'] == 'redux'
        assert any('store' in f for f in result['files_generated'])

    def test_component_mobx_state(self, module):
        """Test component with MobX state management."""
        result = module.execute_component(context={}, state='mobx')
        assert result['state_management'] == 'mobx'
        assert any('store' in f for f in result['files_generated'])

    def test_component_zustand_state(self, module):
        """Test component with Zustand state management."""
        result = module.execute_component(context={}, state='zustand')
        assert result['state_management'] == 'zustand'
        assert any('store' in f for f in result['files_generated'])

    def test_component_with_storybook(self, module):
        """Test component with Storybook stories."""
        result = module.execute_component(context={}, storybook=True)
        assert any('stories' in f for f in result['files_generated'])

    def test_component_vue_framework(self, module):
        """Test component with Vue framework."""
        result = module.execute_component(context={}, framework='vue')
        assert result['framework'] == 'vue'

    def test_component_class_type(self, module):
        """Test class component type."""
        result = module.execute_component(context={}, type='class')
        assert result['type'] == 'class'

    def test_component_accessibility_setting(self, module):
        """Test accessibility configuration."""
        result = module.execute_component(context={}, accessibility='wcag_aaa')
        assert result['accessibility'] == 'wcag_aaa'

    def test_component_responsive_setting(self, module):
        """Test responsive configuration."""
        result = module.execute_component(context={}, responsive=False)
        assert result['responsive'] is False

    def test_component_with_props(self, module):
        """Test component with props."""
        result = module.execute_component(context={}, props=['title', 'onClick'])
        assert 'props' in result


class TestDashboardCommand:
    """Test execute_dashboard command."""

    def test_dashboard_defaults(self, module):
        """Test dashboard with default settings."""
        result = module.execute_dashboard(context={})
        assert result['layout'] == 'grid'
        assert result['theme'] == 'light'
        assert result['responsive'] is True
        assert 'components' in result
        assert 'navigation' in result['components']
        assert 'header' in result['components']
        assert 'main' in result['components']

    def test_dashboard_dark_theme(self, module):
        """Test dashboard with dark theme."""
        result = module.execute_dashboard(context={}, theme='dark')
        assert result['theme'] == 'dark'

    def test_dashboard_flex_layout(self, module):
        """Test dashboard with flex layout."""
        result = module.execute_dashboard(context={}, layout='flex')
        assert result['layout'] == 'flex'

    def test_dashboard_custom_nav(self, module):
        """Test dashboard with custom navigation."""
        result = module.execute_dashboard(context={}, nav_type='topbar', nav_items=['Home', 'Reports'])
        assert result['components']['navigation']['type'] == 'topbar'
        assert 'Home' in result['components']['navigation']['items']

    def test_dashboard_header_options(self, module):
        """Test dashboard header options."""
        result = module.execute_dashboard(context={}, search=False, user_menu=False, notifications=False)
        assert result['components']['header']['include_search'] is False
        assert result['components']['header']['user_menu'] is False
        assert result['components']['header']['notifications'] is False

    def test_dashboard_custom_columns(self, module):
        """Test dashboard with custom columns."""
        result = module.execute_dashboard(context={}, columns=6, gap=24)
        assert result['components']['main']['columns'] == 6
        assert result['components']['main']['gap'] == 24

    def test_dashboard_charts(self, module):
        """Test dashboard with charts configuration."""
        result = module.execute_dashboard(context={}, charts=['donut', 'scatter'])
        assert 'donut' in result['charts']
        assert 'scatter' in result['charts']

    def test_dashboard_refresh_interval(self, module):
        """Test dashboard with custom refresh interval."""
        result = module.execute_dashboard(context={}, refresh_interval=60)
        assert result['data_refresh'] == 60

    def test_dashboard_real_time(self, module):
        """Test dashboard with real-time updates."""
        result = module.execute_dashboard(context={}, real_time=True)
        assert result['real_time'] is True

    def test_dashboard_export_formats(self, module):
        """Test dashboard includes export formats."""
        result = module.execute_dashboard(context={})
        assert 'pdf' in result['export_formats']
        assert 'csv' in result['export_formats']


class TestFormCommand:
    """Test execute_form command."""

    def test_form_defaults(self, module):
        """Test form with default settings."""
        result = module.execute_form(context={})
        assert result['validation_library'] == 'yup'
        assert 'fields' in result

    def test_form_with_fields(self, module):
        """Test form with custom fields."""
        result = module.execute_form(context={}, fields=['name', 'email', 'password'])
        assert 'fields' in result
        assert len(result['fields']) == 3

    def test_form_zod_validation(self, module):
        """Test form with Zod validation."""
        result = module.execute_form(context={}, validation='zod')
        assert result['validation_library'] == 'zod'


class TestAccessibilityCommand:
    """Test execute_accessibility command."""

    def test_accessibility_defaults(self, module):
        """Test accessibility with default settings."""
        result = module.execute_accessibility(context={})
        assert 'level' in result
        assert 'features' in result

    def test_accessibility_wcag_aaa(self, module):
        """Test accessibility with WCAG AAA level."""
        result = module.execute_accessibility(context={}, level='wcag_aaa')
        assert result['level'] == 'wcag_aaa'


class TestResponsiveCommand:
    """Test execute_responsive command."""

    def test_responsive_defaults(self, module):
        """Test responsive with default settings."""
        result = module.execute_responsive(context={})
        assert 'breakpoints' in result
        assert 'container_max_widths' in result

    def test_responsive_custom_breakpoints(self, module):
        """Test responsive with custom breakpoints."""
        result = module.execute_responsive(context={}, breakpoints={'sm': 640, 'md': 768, 'lg': 1024})
        assert 'breakpoints' in result


class TestThemeCommand:
    """Test execute_theme command."""

    def test_theme_defaults(self, module):
        """Test theme with default settings."""
        result = module.execute_theme(context={})
        assert 'colors' in result
        assert 'typography' in result

    def test_theme_dark_mode(self, module):
        """Test theme with dark mode."""
        result = module.execute_theme(context={}, dark_mode=True)
        assert result['dark_mode'] is True

    def test_theme_custom_primary(self, module):
        """Test theme with custom primary color."""
        result = module.execute_theme(context={}, primary_color='#ff6600')
        assert result['colors']['primary'] == '#ff6600'


class TestAnimationCommand:
    """Test execute_animation command."""

    def test_animation_defaults(self, module):
        """Test animation with default settings."""
        result = module.execute_animation(context={})
        assert 'type' in result
        assert 'duration' in result

    def test_animation_custom_type(self, module):
        """Test animation with custom type."""
        result = module.execute_animation(context={}, type='slide', duration=500)
        assert result['type'] == 'slide'
        assert result['duration'] == 500


class TestLayoutCommand:
    """Test execute_layout command."""

    def test_layout_defaults(self, module):
        """Test layout with default settings."""
        result = module.execute_layout(context={})
        assert isinstance(result, dict)

    def test_layout_grid_type(self, module):
        """Test layout with grid type."""
        result = module.execute_layout(context={}, type='grid')
        assert isinstance(result, dict)

    def test_layout_responsive(self, module):
        """Test layout with responsive breakpoints."""
        result = module.execute_layout(context={}, responsive=True)
        assert 'breakpoints' in result
