"""
🎯 Button Manager - Sistema de Gestión de Botones AsistoYA
Manejo centralizado de botones, eventos y estado de la aplicación
"""

import tkinter as tk
from tkinter import ttk
import ttkbootstrap as ttk_bootstrap
from ttkbootstrap.constants import *
import logging
from typing import Dict, Callable, Optional, Any, List
from datetime import datetime
import threading
from functools import wraps

class ButtonState:
    """Estados posibles de un botón"""
    ENABLED = "enabled"
    DISABLED = "disabled"
    LOADING = "loading"
    ERROR = "error"
    SUCCESS = "success"

class ButtonConfig:
    """Configuración de un botón"""
    def __init__(self, 
                 button_id: str,
                 text: str,
                 command: Callable,
                 style: str = PRIMARY,
                 tooltip: str = "",
                 permissions: List[str] = None,
                 validation_func: Callable = None,
                 error_handler: Callable = None):
        self.button_id = button_id
        self.text = text
        self.command = command
        self.style = style
        self.tooltip = tooltip
        self.permissions = permissions or []
        self.validation_func = validation_func
        self.error_handler = error_handler
        self.state = ButtonState.ENABLED
        self.last_clicked = None
        self.click_count = 0

class ButtonManager:
    """Gestor centralizado de botones"""
    
    def __init__(self, app_instance=None):
        self.app = app_instance
        self.buttons: Dict[str, ButtonConfig] = {}
        self.button_widgets: Dict[str, ttk_bootstrap.Button] = {}
        self.logger = self._setup_logger()
        self.state_callbacks: Dict[str, List[Callable]] = {}
        self.global_state = "normal"
        
    def _setup_logger(self):
        """Configurar logging para depuración"""
        logger = logging.getLogger('ButtonManager')
        logger.setLevel(logging.DEBUG)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '🎯 %(asctime)s - ButtonManager - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def register_button(self, config: ButtonConfig) -> None:
        """Registrar una nueva configuración de botón"""
        self.buttons[config.button_id] = config
        self.logger.debug(f"Botón registrado: {config.button_id} - {config.text}")
    
    def create_button(self, parent, button_id: str, **kwargs) -> ttk_bootstrap.Button:
        """Crear un botón con manejo automático de eventos"""
        if button_id not in self.buttons:
            raise ValueError(f"Botón no registrado: {button_id}")
        
        config = self.buttons[button_id]
        
        # Crear comando wrapeado con manejo de errores
        wrapped_command = self._wrap_command(config)
        
        # Crear botón
        button = ttk_bootstrap.Button(
            parent,
            text=config.text,
            command=wrapped_command,
            bootstyle=config.style,
            **kwargs
        )
        
        # Almacenar referencia
        self.button_widgets[button_id] = button
        
        # Configurar tooltip si existe
        if config.tooltip:
            self._add_tooltip(button, config.tooltip)
        
        # Verificar permisos iniciales
        self._update_button_permissions(button_id)
        
        self.logger.debug(f"🎯 Botón creado: {button_id}")
        return button
    
    def _wrap_command(self, config: ButtonConfig) -> Callable:
        """Envolver comando con manejo de errores y logging"""
        @wraps(config.command)
        def wrapped_command():
            try:
                # Log del click
                self.logger.info(f"🖱️ Click en botón: {config.button_id}")
                config.click_count += 1
                config.last_clicked = datetime.now()
                
                # Verificar validación previa
                if config.validation_func and not config.validation_func():
                    self.logger.warning(f"Validación fallida para: {config.button_id}")
                    return
                
                # Verificar permisos
                if not self._check_permissions(config):
                    self.logger.warning(f"Permisos insuficientes para: {config.button_id}")
                    return
                
                # Cambiar estado a loading
                self.set_button_state(config.button_id, ButtonState.LOADING)
                  # Ejecutar comando en hilo separado para UI responsiva
                def execute_command():
                    try:
                        result = config.command()
                        
                        # Cambiar estado a success usando after para thread safety
                        if self.app_instance and hasattr(self.app_instance, 'root'):
                            self.app_instance.root.after(0, self.set_button_state, config.button_id, ButtonState.SUCCESS)
                        
                        # Volver a estado normal después de 2 segundos
                        if self.app_instance and hasattr(self.app_instance, 'root'):
                            self.app_instance.root.after(2000, self.set_button_state, config.button_id, ButtonState.ENABLED)
                        
                        self.logger.info(f"Comando ejecutado exitosamente: {config.button_id}")
                        
                    except Exception as e:
                        self.logger.error(f"Error en comando {config.button_id}: {str(e)}")
                        
                        # Cambiar estado a error usando after para thread safety
                        if self.app_instance and hasattr(self.app_instance, 'root'):
                            self.app_instance.root.after(0, self.set_button_state, config.button_id, ButtonState.ERROR)
                        
                        # Manejar error
                        if config.error_handler:
                            config.error_handler(e)
                        
                        # Volver a estado normal después de 3 segundos
                        if self.app_instance and hasattr(self.app_instance, 'root'):
                            self.app_instance.root.after(3000, self.set_button_state, config.button_id, ButtonState.ENABLED)
                
                # Ejecutar en hilo separado
                threading.Thread(target=execute_command, daemon=True).start()
                
            except Exception as e:
                self.logger.error(f"Error crítico en botón {config.button_id}: {str(e)}")
                self.set_button_state(config.button_id, ButtonState.ERROR)
        
        return wrapped_command
    
    def set_button_state(self, button_id: str, state: ButtonState) -> None:
        """Cambiar estado de un botón"""
        if button_id not in self.buttons:
            return
        
        config = self.buttons[button_id]
        config.state = state
        
        if button_id in self.button_widgets:
            button = self.button_widgets[button_id]
            
            if state == ButtonState.DISABLED:
                button.configure(state="disabled")
            elif state == ButtonState.LOADING:
                button.configure(text="Cargando...", state="disabled")
            elif state == ButtonState.ERROR:
                button.configure(text="Error", bootstyle=DANGER)
            elif state == ButtonState.SUCCESS:
                button.configure(text="Completado", bootstyle=SUCCESS)
            elif state == ButtonState.ENABLED:
                button.configure(
                    text=config.text, 
                    bootstyle=config.style,
                    state="normal"
                )
        
        # Ejecutar callbacks de estado
        self._execute_state_callbacks(button_id, state)
        
        self.logger.debug(f"Estado cambiado: {button_id} -> {state}")
    
    def _check_permissions(self, config: ButtonConfig) -> bool:
        """Verificar permisos para ejecutar comando"""
        if not config.permissions or not self.app:
            return True
        
        # Verificar con el sistema de autenticación
        if hasattr(self.app, 'auth_manager') and hasattr(self.app, 'user'):
            user_role = self.app.user.get('role', 'user')
            for permission in config.permissions:
                if not self.app.auth_manager.has_permission(user_role, permission):
                    return False
        
        return True
    
    def _update_button_permissions(self, button_id: str) -> None:
        """Actualizar estado del botón basado en permisos"""
        if button_id not in self.buttons:
            return
        
        config = self.buttons[button_id]
        has_permission = self._check_permissions(config)
        
        if has_permission:
            self.set_button_state(button_id, ButtonState.ENABLED)
        else:
            self.set_button_state(button_id, ButtonState.DISABLED)
    
    def update_all_permissions(self) -> None:
        """Actualizar permisos de todos los botones"""
        for button_id in self.buttons:
            self._update_button_permissions(button_id)
    
    def _add_tooltip(self, widget, text: str) -> None:
        """Agregar tooltip a un widget"""
        def show_tooltip(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            
            label = tk.Label(
                tooltip,
                text=text,
                background="yellow",
                relief="solid",
                borderwidth=1,
                font=("Arial", 8)
            )
            label.pack()
            
            def hide_tooltip():
                tooltip.destroy()
            
            tooltip.after(3000, hide_tooltip)  # Auto-hide después de 3 segundos
        
        widget.bind("<Enter>", show_tooltip)
    
    def add_state_callback(self, button_id: str, callback: Callable) -> None:
        """Agregar callback para cambios de estado"""
        if button_id not in self.state_callbacks:
            self.state_callbacks[button_id] = []
        self.state_callbacks[button_id].append(callback)
    
    def _execute_state_callbacks(self, button_id: str, state: ButtonState) -> None:
        """Ejecutar callbacks de cambio de estado"""
        if button_id in self.state_callbacks:
            for callback in self.state_callbacks[button_id]:
                try:
                    callback(button_id, state)
                except Exception as e:
                    self.logger.error(f"Error en callback de estado: {e}")
    
    def get_button_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas de uso de botones"""
        stats = {}
        for button_id, config in self.buttons.items():
            stats[button_id] = {
                'clicks': config.click_count,
                'last_clicked': config.last_clicked,
                'current_state': config.state,
                'text': config.text
            }
        return stats
    
    def reset_button_stats(self) -> None:
        """Resetear estadísticas de botones"""
        for config in self.buttons.values():
            config.click_count = 0
            config.last_clicked = None
        self.logger.info("📊 Estadísticas de botones reseteadas")
    
    def enable_debug_mode(self) -> None:
        """Habilitar modo debug con información extra"""
        self.logger.setLevel(logging.DEBUG)
        self.logger.info("🐛 Modo debug habilitado para ButtonManager")
    
    def disable_all_buttons(self) -> None:
        """Deshabilitar todos los botones"""
        for button_id in self.buttons:
            self.set_button_state(button_id, ButtonState.DISABLED)
        self.global_state = "disabled"
        self.logger.info("Todos los botones deshabilitados")
    
    def enable_all_buttons(self) -> None:
        """Habilitar todos los botones"""
        for button_id in self.buttons:
            self.set_button_state(button_id, ButtonState.ENABLED)
        self.global_state = "normal"
        self.logger.info("Todos los botones habilitados")
    
    def cleanup(self) -> None:
        """Limpiar recursos y event listeners"""
        self.logger.info("🧹 Limpiando ButtonManager...")
        self.buttons.clear()
        self.button_widgets.clear()
        self.state_callbacks.clear()

# Instancia global del gestor de botones
button_manager = ButtonManager()

def get_button_manager() -> ButtonManager:
    """Obtener instancia global del gestor de botones"""
    return button_manager