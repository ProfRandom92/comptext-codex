"""Module K: Frontend/UI - Component scaffolding, accessibility, responsive design."""

from typing import Any, Dict, List

from comptext_codex.registry import codex_module, codex_command
from .base import BaseModule


@codex_module(
    code="K",
    name="Frontend/UI",
    purpose="Component scaffolding, accessibility, and responsive design",
    token_priority="medium",
    security={"pii_safe": True, "threat_model": "xss_prevention"},
    privacy={"dp_budget": "epsilon<=1.0_per_call"},
)
class ModuleK(BaseModule):
    """Frontend/UI module for component generation."""

    @codex_command(syntax="@COMPONENT[framework, type, ...]", description="Generate UI component with configuration", token_cost_hint=65)
    def execute_component(self, *args, context: Dict[str, Any] = None, **kwargs) -> Dict[str, Any]:
        """Generate UI component with comprehensive configuration."""
        framework = kwargs.get('framework', 'react')
        comp_type = kwargs.get('type', 'functional')
        styling = kwargs.get('styling', 'css-modules')
        typescript = kwargs.get('typescript', True)
        state = kwargs.get('state', 'local')

        extension = 'tsx' if typescript else 'jsx'
        test_framework = kwargs.get('test_framework', 'jest')

        files = [
            f'Component.{extension}',
            f'Component.test.{extension}',
            f'Component.module.{styling}' if 'modules' in styling else f'Component.{styling}',
        ]

        if state in ['redux', 'mobx', 'zustand']:
            files.append(f'Component.store.{extension}')

        if kwargs.get('storybook', False):
            files.append(f'Component.stories.{extension}')

        return {
            'framework': framework,
            'type': comp_type,
            'styling': styling,
            'typescript': typescript,
            'state_management': state,
            'files_generated': files,
            'accessibility': kwargs.get('accessibility', 'wcag_aa'),
            'responsive': kwargs.get('responsive', True),
            'props': self._generate_prop_types(kwargs.get('props', [])),
            'hooks': self._recommend_hooks(comp_type, state),
            'dependencies': self._get_dependencies(framework, styling, state)
        }

    @codex_command(syntax="@DASHBOARD[layout, theme, ...]", description="Generate comprehensive dashboard layout", token_cost_hint=70)
    def execute_dashboard(self, *args, context: Dict[str, Any] = None, **kwargs) -> Dict[str, Any]:
        layout = kwargs.get('layout', 'grid')
        theme = kwargs.get('theme', 'light')
        responsive = kwargs.get('responsive', True)

        components = {
            'navigation': {
                'type': kwargs.get('nav_type', 'sidebar'),
                'items': kwargs.get('nav_items', ['Dashboard', 'Analytics', 'Settings'])
            },
            'header': {
                'include_search': kwargs.get('search', True),
                'user_menu': kwargs.get('user_menu', True),
                'notifications': kwargs.get('notifications', True)
            },
            'main': {
                'layout': layout,
                'columns': kwargs.get('columns', 12),
                'gap': kwargs.get('gap', 16)
            },
            'widgets': self._generate_widget_config(kwargs)
        }

        return {
            'layout': layout,
            'theme': theme,
            'responsive': responsive,
            'components': components,
            'charts': kwargs.get('charts', ['line', 'bar', 'pie', 'area']),
            'data_refresh': kwargs.get('refresh_interval', 30),
            'export_formats': ['pdf', 'csv', 'excel'],
            'filters': self._generate_filter_config(kwargs),
            'real_time': kwargs.get('real_time', False),
            'mobile_optimized': responsive
        }

    @codex_command(syntax="@FORM[fields, validation, ...]", description="Generate form with validation and accessibility", token_cost_hint=60)
    def execute_form(self, *args, context: Dict[str, Any] = None, **kwargs) -> Dict[str, Any]:
        fields = kwargs.get('fields', [])
        validation = kwargs.get('validation', 'yup')

        field_configs = []
        for field in fields:
            field_configs.append({
                'name': field,
                'type': self._infer_field_type(field),
                'validation': self._generate_validation_rules(field),
                'accessibility': {
                    'label': field.replace('_', ' ').title(),
                    'aria-label': f'Enter {field}',
                    'required': True
                }
            })

        return {
            'fields': field_configs,
            'validation_library': validation,
            'submit_handler': 'async',
            'error_handling': 'field-level',
            'accessibility_features': [
                'keyboard_navigation',
                'screen_reader_support',
                'error_announcements',
                'focus_management'
            ],
            'features': {
                'auto_save': kwargs.get('auto_save', False),
                'multi_step': kwargs.get('multi_step', False),
                'file_upload': 'drag_drop' if kwargs.get('file_upload') else None
            }
        }

    @codex_command(syntax="@LAYOUT[type, responsive, ...]", description="Generate responsive layout structure", token_cost_hint=50)
    def execute_layout(self, *args, context: Dict[str, Any] = None, **kwargs) -> Dict[str, Any]:
        layout_type = kwargs.get('type', 'flex')
        responsive = kwargs.get('responsive', True)

        layouts = {
            'flex': self._generate_flex_layout(kwargs),
            'grid': self._generate_grid_layout(kwargs),
            'masonry': self._generate_masonry_layout(kwargs),
            'split': self._generate_split_layout(kwargs)
        }

        layout_config = layouts.get(layout_type, layouts['flex'])

        if responsive:
            layout_config['breakpoints'] = {
                'mobile': '320px',
                'tablet': '768px',
                'desktop': '1024px',
                'wide': '1440px'
            }

        return layout_config

    @codex_command(syntax="@THEME[colors, typography, ...]", description="Generate comprehensive theme configuration", token_cost_hint=55)
    def execute_theme(self, *args, context: Dict[str, Any] = None, **kwargs) -> Dict[str, Any]:
        base_color = kwargs.get('primary_color', '#3b82f6')

        return {
            'colors': {
                'primary': base_color,
                'secondary': kwargs.get('secondary_color', '#8b5cf6'),
                'accent': kwargs.get('accent_color', '#06b6d4'),
                'success': '#10b981',
                'warning': '#f59e0b',
                'error': '#ef4444',
                'neutral': self._generate_neutral_scale()
            },
            'typography': {
                'font_family': kwargs.get('font_family', 'Inter, system-ui, sans-serif'),
                'scale': self._generate_type_scale(),
                'weights': {'light': 300, 'regular': 400, 'medium': 500, 'semibold': 600, 'bold': 700}
            },
            'spacing': self._generate_spacing_scale(),
            'shadows': self._generate_shadow_scale(),
            'borders': {
                'radius': {'sm': '4px', 'md': '8px', 'lg': '12px', 'xl': '16px', 'full': '9999px'},
                'width': {'thin': '1px', 'medium': '2px', 'thick': '4px'}
            },
            'animations': {
                'duration': {'fast': '150ms', 'normal': '300ms', 'slow': '500ms'},
                'easing': {
                    'ease_in': 'cubic-bezier(0.4, 0, 1, 1)',
                    'ease_out': 'cubic-bezier(0, 0, 0.2, 1)',
                    'ease_in_out': 'cubic-bezier(0.4, 0, 0.2, 1)'
                }
            },
            'dark_mode': kwargs.get('dark_mode', True),
            'css_variables': True
        }

    @codex_command(syntax="@ANIMATION[type, duration, ...]", description="Generate animation configuration", token_cost_hint=40)
    def execute_animation(self, *args, context: Dict[str, Any] = None, **kwargs) -> Dict[str, Any]:
        anim_type = kwargs.get('type', 'fade')
        duration = kwargs.get('duration', 300)

        animations = {
            'fade': {'opacity': [0, 1]},
            'slide': {'transform': ['translateY(20px)', 'translateY(0)']},
            'scale': {'transform': ['scale(0.9)', 'scale(1)']},
            'bounce': {'transform': ['scale(0.8)', 'scale(1.1)', 'scale(1)']},
            'rotate': {'transform': ['rotate(0deg)', 'rotate(360deg)']}
        }

        return {
            'type': anim_type,
            'keyframes': animations.get(anim_type, animations['fade']),
            'duration': duration,
            'timing_function': kwargs.get('easing', 'ease-in-out'),
            'delay': kwargs.get('delay', 0),
            'iteration_count': kwargs.get('iterations', 1),
            'direction': kwargs.get('direction', 'normal'),
            'fill_mode': 'both'
        }

    @codex_command(syntax="@RESPONSIVE[breakpoints, ...]", description="Generate responsive design configuration", token_cost_hint=45)
    def execute_responsive(self, *args, context: Dict[str, Any] = None, **kwargs) -> Dict[str, Any]:
        breakpoints = kwargs.get('breakpoints', {
            'xs': '320px',
            'sm': '640px',
            'md': '768px',
            'lg': '1024px',
            'xl': '1280px',
            '2xl': '1536px'
        })

        return {
            'breakpoints': breakpoints,
            'container_max_widths': {
                'sm': '640px',
                'md': '768px',
                'lg': '1024px',
                'xl': '1280px'
            },
            'fluid_typography': self._generate_fluid_typography(),
            'responsive_images': {
                'srcset': True,
                'lazy_loading': True,
                'webp_support': True
            },
            'mobile_first': kwargs.get('mobile_first', True),
            'touch_optimized': {
                'min_tap_target': '44px',
                'swipe_gestures': kwargs.get('gestures', True)
            }
        }

    @codex_command(syntax="@ACCESSIBILITY[level, features, ...]", description="Generate accessibility configuration", token_cost_hint=50)
    def execute_accessibility(self, *args, context: Dict[str, Any] = None, **kwargs) -> Dict[str, Any]:
        level = kwargs.get('level', 'wcag_aa')

        return {
            'level': level,
            'features': {
                'semantic_html': True,
                'aria_labels': True,
                'keyboard_navigation': True,
                'focus_indicators': True,
                'skip_links': True,
                'screen_reader_support': True
            },
            'color_contrast': {
                'minimum_ratio': 4.5 if level == 'wcag_aa' else 7,
                'large_text_ratio': 3 if level == 'wcag_aa' else 4.5
            },
            'interactive_elements': {
                'min_size': '44x44px',
                'spacing': '8px',
                'clear_focus_state': True
            },
            'forms': {
                'labels_for_inputs': True,
                'error_identification': True,
                'instructions_provided': True
            },
            'media': {
                'alt_text': True,
                'captions': kwargs.get('captions', True),
                'audio_descriptions': kwargs.get('audio_desc', False)
            },
            'testing': {
                'automated_tools': ['axe', 'lighthouse'],
                'manual_checks': True
            }
        }

    # Helper methods

    def _generate_prop_types(self, props: List[str]) -> Dict[str, str]:
        """Generate prop type definitions."""
        return {prop: self._infer_prop_type(prop) for prop in props}

    def _infer_prop_type(self, prop: str) -> str:
        """Infer prop type from name."""
        if 'count' in prop or 'id' in prop or 'index' in prop:
            return 'number'
        elif 'is' in prop or 'has' in prop or 'show' in prop:
            return 'boolean'
        elif 'callback' in prop or 'handler' in prop or prop.startswith('on'):
            return 'function'
        elif 'list' in prop or 'items' in prop:
            return 'array'
        elif 'data' in prop or 'config' in prop:
            return 'object'
        return 'string'

    def _recommend_hooks(self, comp_type: str, state: str) -> List[str]:
        """Recommend React hooks based on component type."""
        hooks = ['useState', 'useEffect']

        if state == 'redux':
            hooks.extend(['useSelector', 'useDispatch'])
        elif state == 'context':
            hooks.append('useContext')

        if comp_type == 'performance':
            hooks.extend(['useMemo', 'useCallback'])

        return hooks

    def _get_dependencies(self, framework: str, styling: str, state: str) -> List[str]:
        """Get required dependencies."""
        deps = [framework]

        if styling == 'styled-components':
            deps.append('styled-components')
        elif styling == 'emotion':
            deps.append('@emotion/react')
        elif styling == 'tailwind':
            deps.append('tailwindcss')

        if state == 'redux':
            deps.extend(['redux', 'react-redux', '@reduxjs/toolkit'])
        elif state == 'mobx':
            deps.extend(['mobx', 'mobx-react-lite'])
        elif state == 'zustand':
            deps.append('zustand')

        return deps

    def _generate_widget_config(self, kwargs: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate widget configurations."""
        return [
            {'type': 'stats', 'size': 'col-span-3', 'data_source': 'metrics'},
            {'type': 'chart', 'size': 'col-span-8', 'chart_type': 'line'},
            {'type': 'table', 'size': 'col-span-12', 'sortable': True, 'filterable': True}
        ]

    def _generate_filter_config(self, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Generate filter configuration."""
        return {
            'date_range': True,
            'search': True,
            'categories': kwargs.get('filter_categories', []),
            'custom_filters': kwargs.get('custom_filters', [])
        }

    def _infer_field_type(self, field: str) -> str:
        """Infer input field type from name."""
        if 'email' in field.lower():
            return 'email'
        elif 'password' in field.lower():
            return 'password'
        elif 'phone' in field.lower():
            return 'tel'
        elif 'date' in field.lower():
            return 'date'
        elif 'number' in field.lower() or 'age' in field.lower():
            return 'number'
        elif 'url' in field.lower() or 'website' in field.lower():
            return 'url'
        return 'text'

    def _generate_validation_rules(self, field: str) -> Dict[str, Any]:
        """Generate validation rules for field."""
        rules = {'required': True}

        if 'email' in field.lower():
            rules['email'] = True
        elif 'password' in field.lower():
            rules['minLength'] = 8
            rules['pattern'] = '^(?=.*[A-Za-z])(?=.*\\d)[A-Za-z\\d]{8,}$'
        elif 'age' in field.lower():
            rules['min'] = 0
            rules['max'] = 150

        return rules

    def _generate_flex_layout(self, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Generate flexbox layout config."""
        return {
            'type': 'flex',
            'direction': kwargs.get('direction', 'row'),
            'justify': kwargs.get('justify', 'space-between'),
            'align': kwargs.get('align', 'center'),
            'wrap': kwargs.get('wrap', True),
            'gap': kwargs.get('gap', 16)
        }

    def _generate_grid_layout(self, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Generate CSS grid layout config."""
        return {
            'type': 'grid',
            'columns': kwargs.get('columns', 12),
            'rows': kwargs.get('rows', 'auto'),
            'gap': kwargs.get('gap', 16),
            'areas': kwargs.get('areas', [])
        }

    def _generate_masonry_layout(self, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Generate masonry layout config."""
        return {
            'type': 'masonry',
            'columns': kwargs.get('columns', 3),
            'gap': kwargs.get('gap', 16),
            'responsive': True
        }

    def _generate_split_layout(self, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Generate split pane layout config."""
        return {
            'type': 'split',
            'orientation': kwargs.get('orientation', 'horizontal'),
            'ratio': kwargs.get('ratio', 0.5),
            'resizable': kwargs.get('resizable', True),
            'min_size': kwargs.get('min_size', 200)
        }

    def _generate_neutral_scale(self) -> Dict[str, str]:
        """Generate neutral color scale."""
        return {
            '50': '#fafafa',
            '100': '#f5f5f5',
            '200': '#e5e5e5',
            '300': '#d4d4d4',
            '400': '#a3a3a3',
            '500': '#737373',
            '600': '#525252',
            '700': '#404040',
            '800': '#262626',
            '900': '#171717'
        }

    def _generate_type_scale(self) -> Dict[str, str]:
        """Generate typographic scale."""
        return {
            'xs': '0.75rem',
            'sm': '0.875rem',
            'base': '1rem',
            'lg': '1.125rem',
            'xl': '1.25rem',
            '2xl': '1.5rem',
            '3xl': '1.875rem',
            '4xl': '2.25rem',
            '5xl': '3rem'
        }

    def _generate_spacing_scale(self) -> Dict[str, str]:
        """Generate spacing scale."""
        return {
            '0': '0',
            '1': '0.25rem',
            '2': '0.5rem',
            '3': '0.75rem',
            '4': '1rem',
            '5': '1.25rem',
            '6': '1.5rem',
            '8': '2rem',
            '10': '2.5rem',
            '12': '3rem',
            '16': '4rem'
        }

    def _generate_shadow_scale(self) -> Dict[str, str]:
        """Generate box shadow scale."""
        return {
            'sm': '0 1px 2px 0 rgb(0 0 0 / 0.05)',
            'md': '0 4px 6px -1px rgb(0 0 0 / 0.1)',
            'lg': '0 10px 15px -3px rgb(0 0 0 / 0.1)',
            'xl': '0 20px 25px -5px rgb(0 0 0 / 0.1)',
            '2xl': '0 25px 50px -12px rgb(0 0 0 / 0.25)'
        }

    def _generate_fluid_typography(self) -> Dict[str, str]:
        """Generate fluid typography using clamp()."""
        return {
            'xs': 'clamp(0.75rem, 0.7rem + 0.25vw, 0.875rem)',
            'sm': 'clamp(0.875rem, 0.825rem + 0.25vw, 1rem)',
            'base': 'clamp(1rem, 0.95rem + 0.25vw, 1.125rem)',
            'lg': 'clamp(1.125rem, 1.05rem + 0.375vw, 1.25rem)',
            'xl': 'clamp(1.25rem, 1.15rem + 0.5vw, 1.5rem)',
            '2xl': 'clamp(1.5rem, 1.35rem + 0.75vw, 1.875rem)'
        }


def get_module() -> ModuleK:
    return ModuleK()
