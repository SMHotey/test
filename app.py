#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Приложение для изучения регламента и тестирования сотрудников.
Режимы: Изучение и Тестирование
"""

import sys
import json
import os
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QRadioButton, QCheckBox, QButtonGroup,
    QScrollArea, QFrame, QStackedWidget, QLineEdit, QComboBox,
    QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView,
    QDialog, QDialogButtonBox, QListWidget, QListWidgetItem,
    QSplitter, QTextEdit, QGroupBox, QFormLayout
)
from PyQt5.QtCore import Qt, QTimer, QTime
from PyQt5.QtGui import QFont, QColor, QPalette

# Пути к файлам данных
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REGLEMENT_FILE = os.path.join(BASE_DIR, "reglament.json")
SCENARIOS_FILE = os.path.join(BASE_DIR, "test_scenarios.json")
RESULTS_FILE = os.path.join(BASE_DIR, "test_results.json")
USER_DATA_FILE = os.path.join(BASE_DIR, "user_data.json")


def load_json(filepath):
    """Загрузка JSON файла."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_json(filepath, data):
    """Сохранение в JSON файл."""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


class ReglamentViewer(QWidget):
    """Виджет для просмотра регламента."""
    
    def __init__(self):
        super().__init__()
        self.reglament_data = load_json(REGLEMENT_FILE)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Заголовок
        title_label = QLabel("Регламент по сопровождению сделок")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(title_label)
        
        version_label = QLabel(f"Версия: {self.reglament_data.get('version', 'N/A')}")
        layout.addWidget(version_label)
        
        # Splitter для навигации и контента
        splitter = QSplitter(Qt.Horizontal)
        
        # Левая панель - навигация по процессам
        nav_widget = QWidget()
        nav_layout = QVBoxLayout(nav_widget)
        nav_label = QLabel("Процессы:")
        nav_label.setFont(QFont("Arial", 12, QFont.Bold))
        nav_layout.addWidget(nav_label)
        
        self.process_list = QListWidget()
        self.process_list.currentRowChanged.connect(self.on_process_selected)
        nav_layout.addWidget(self.process_list)
        
        # Правая панель - содержимое
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        
        self.content_text = QTextEdit()
        self.content_text.setReadOnly(True)
        self.content_text.setFont(QFont("Arial", 11))
        content_layout.addWidget(self.content_text)
        
        splitter.addWidget(nav_widget)
        splitter.addWidget(content_widget)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 3)
        
        layout.addWidget(splitter)
        self.setLayout(layout)
        
        # Заполнение списка процессов
        self.populate_processes()
    
    def populate_processes(self):
        """Заполнение списка процессов."""
        processes = self.reglament_data.get('processes', [])
        for proc in processes:
            item_text = f"{proc.get('id', '')}: {proc.get('title', '')}"
            self.process_list.addItem(item_text)
        
        # Добавление глобальных правил
        if self.reglament_data.get('global_rules'):
            self.process_list.addItem("Глобальные правила")
    
    def on_process_selected(self, index):
        """Обработка выбора процесса."""
        processes = self.reglament_data.get('processes', [])
        
        if index < len(processes):
            proc = processes[index]
            content = self.format_process_content(proc)
        else:
            content = self.format_global_rules()
        
        self.content_text.setHtml(content)
    
    def format_process_content(self, proc):
        """Форматирование содержимого процесса."""
        html = f"<h2>{proc.get('title', '')}</h2>"
        html += f"<p><b>Описание:</b> {proc.get('description', '')}</p>"
        
        # Шаги
        steps = proc.get('steps', [])
        if steps:
            html += "<h3>Шаги:</h3><ol>"
            for step in steps:
                html += f"<li><b>{step.get('title', '')}</b>: {step.get('description', '')}</li>"
            html += "</ol>"
        
        # Условия
        conditions = proc.get('conditions', {})
        if conditions:
            html += "<h3>Условия:</h3><ul>"
            for key, value in conditions.items():
                html += f"<li><b>{key}:</b> {value}</li>"
            html += "</ul>"
        
        # Ограничения
        restrictions = proc.get('restrictions', [])
        if restrictions:
            html += "<h3>Ограничения:</h3><ul>"
            for restr in restrictions:
                color = {"warning": "orange", "info": "blue", "forbidden": "red", "important": "purple"}.get(restr.get('type'), 'black')
                html += f"<li style='color: {color};'><b>[{restr.get('type', '')}]</b> {restr.get('text', '')}</li>"
            html += "</ul>"
        
        # Шаблоны
        templates = proc.get('templates', {})
        if templates:
            html += "<h3>Шаблоны:</h3>"
            for name, template in templates.items():
                html += f"<p><b>{name}:</b></p>"
                html += f"<p>Тема: {template.get('subject', '')}</p>"
                html += f"<p>Тело: {template.get('body', '').replace(chr(10), '<br>')}</p>"
        
        return html
    
    def format_global_rules(self):
        """Форматирование глобальных правил."""
        rules = self.reglament_data.get('global_rules', {})
        html = "<h2>Глобальные правила</h2>"
        
        if 'date_rule' in rules:
            rule = rules['date_rule']
            html += f"<h3>Правило дат:</h3><p>{rule.get('description', '')}</p>"
        
        if 'individual_entrepreneur_mark' in rules:
            rule = rules['individual_entrepreneur_mark']
            html += f"<h3>Пометка ИП:</h3><p>{rule.get('rule', '')}</p>"
            html += f"<p><i>Реализация:</i> {rule.get('implementation', '')}</p>"
        
        return html


class QuestionWidget(QWidget):
    """Базовый виджет для вопроса."""
    
    def __init__(self, question_data, parent=None):
        super().__init__(parent)
        self.question_data = question_data
        self.user_answer = None
        self.init_ui()
    
    def init_ui(self):
        raise NotImplementedError
    
    def get_answer(self):
        """Получить ответ пользователя."""
        return self.user_answer
    
    def set_answer(self, answer):
        """Установить ответ (для восстановления)."""
        self.user_answer = answer


class SingleChoiceWidget(QuestionWidget):
    """Вопрос с одним правильным ответом."""
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        q_label = QLabel(self.question_data['question'])
        q_label.setFont(QFont("Arial", 11, QFont.Bold))
        layout.addWidget(q_label)
        
        self.button_group = QButtonGroup(self)
        self.radio_buttons = []
        
        for i, option in enumerate(self.question_data['options']):
            rb = QRadioButton(option)
            rb.toggled.connect(lambda checked, idx=i: self.on_option_toggled(idx, checked))
            self.radio_buttons.append(rb)
            self.button_group.addButton(rb, i)
            layout.addWidget(rb)
        
        self.setLayout(layout)
    
    def on_option_toggled(self, idx, checked):
        if checked:
            self.user_answer = [idx]
    
    def get_answer(self):
        if self.user_answer is None:
            for i, rb in enumerate(self.radio_buttons):
                if rb.isChecked():
                    return [i]
        return self.user_answer
    
    def set_answer(self, answer):
        self.user_answer = answer
        if answer and isinstance(answer, list) and len(answer) > 0:
            self.radio_buttons[answer[0]].setChecked(True)


class MultipleChoiceWidget(QuestionWidget):
    """Вопрос с несколькими правильными ответами."""
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        q_label = QLabel(self.question_data['question'])
        q_label.setFont(QFont("Arial", 11, QFont.Bold))
        layout.addWidget(q_label)
        
        self.checkboxes = []
        for i, option in enumerate(self.question_data['options']):
            cb = QCheckBox(option)
            cb.stateChanged.connect(lambda state, idx=i: self.on_checkbox_changed(idx, state))
            self.checkboxes.append(cb)
            layout.addWidget(cb)
        
        self.setLayout(layout)
        self.user_answer = []
    
    def on_checkbox_changed(self, idx, state):
        if state == Qt.Checked:
            if idx not in self.user_answer:
                self.user_answer.append(idx)
        else:
            if idx in self.user_answer:
                self.user_answer.remove(idx)
    
    def get_answer(self):
        answer = []
        for i, cb in enumerate(self.checkboxes):
            if cb.isChecked():
                answer.append(i)
        return answer
    
    def set_answer(self, answer):
        self.user_answer = answer or []
        for i, cb in enumerate(self.checkboxes):
            cb.setChecked(i in (answer or []))


class TrueFalseWidget(QuestionWidget):
    """Вопрос Верно/Неверно."""
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        q_label = QLabel(self.question_data['question'])
        q_label.setFont(QFont("Arial", 11, QFont.Bold))
        layout.addWidget(q_label)
        
        self.button_group = QButtonGroup(self)
        
        self.rb_true = QRadioButton("Верно")
        self.rb_false = QRadioButton("Неверно")
        
        self.rb_true.toggled.connect(lambda checked: self.on_choice(checked, True))
        self.rb_false.toggled.connect(lambda checked: self.on_choice(checked, False))
        
        self.button_group.addButton(self.rb_true, 0)
        self.button_group.addButton(self.rb_false, 1)
        
        layout.addWidget(self.rb_true)
        layout.addWidget(self.rb_false)
        
        self.setLayout(layout)
    
    def on_choice(self, checked, value):
        if checked:
            self.user_answer = value
    
    def get_answer(self):
        if self.rb_true.isChecked():
            return True
        elif self.rb_false.isChecked():
            return False
        return self.user_answer
    
    def set_answer(self, answer):
        self.user_answer = answer
        if answer is True:
            self.rb_true.setChecked(True)
        elif answer is False:
            self.rb_false.setChecked(True)


class OrderingWidget(QuestionWidget):
    """Вопрос на упорядочивание элементов."""
    
    def __init__(self, question_data, parent=None):
        self.initial_order = list(range(len(question_data['options'])))
        super().__init__(question_data, parent)
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        q_label = QLabel(self.question_data['question'])
        q_label.setFont(QFont("Arial", 11, QFont.Bold))
        layout.addWidget(q_label)
        
        hint_label = QLabel("Используйте кнопки «Вверх» и «Вниз» для изменения порядка:")
        layout.addWidget(hint_label)
        
        self.order_container = QVBoxLayout()
        self.order_widgets = []
        
        for i, option in enumerate(self.question_data['options']):
            item_widget = self.create_order_item(i, option)
            self.order_widgets.append(item_widget)
            self.order_container.addWidget(item_widget)
        
        layout.addLayout(self.order_container)
        self.setLayout(layout)
        
        self.current_order = self.initial_order.copy()
    
    def create_order_item(self, original_idx, text):
        widget = QFrame()
        widget.setFrameStyle(QFrame.Box | QFrame.Raised)
        layout = QHBoxLayout(widget)
        
        label = QLabel(text)
        layout.addWidget(label)
        
        btn_layout = QVBoxLayout()
        up_btn = QPushButton("▲")
        down_btn = QPushButton("▼")
        up_btn.setFixedWidth(40)
        down_btn.setFixedWidth(40)
        
        up_btn.clicked.connect(lambda: self.move_item_up(original_idx))
        down_btn.clicked.connect(lambda: self.move_item_down(original_idx))
        
        btn_layout.addWidget(up_btn)
        btn_layout.addWidget(down_btn)
        layout.addLayout(btn_layout)
        
        return widget
    
    def move_item_up(self, original_idx):
        current_pos = self.current_order.index(original_idx)
        if current_pos > 0:
            self.current_order[current_pos], self.current_order[current_pos - 1] = \
                self.current_order[current_pos - 1], self.current_order[current_pos]
            self.reorder_widgets()
    
    def move_item_down(self, original_idx):
        current_pos = self.current_order.index(original_idx)
        if current_pos < len(self.current_order) - 1:
            self.current_order[current_pos], self.current_order[current_pos + 1] = \
                self.current_order[current_pos + 1], self.current_order[current_pos]
            self.reorder_widgets()
    
    def reorder_widgets(self):
        # Удаляем все виджеты из layout
        while self.order_container.count():
            item = self.order_container.takeAt(0)
            if item.widget():
                item.widget().setParent(None)
        
        # Добавляем в новом порядке
        for orig_idx in self.current_order:
            self.order_container.addWidget(self.order_widgets[orig_idx])
    
    def get_answer(self):
        return self.current_order
    
    def set_answer(self, answer):
        if answer:
            self.current_order = answer.copy()
            self.reorder_widgets()


class TestScenarioWidget(QWidget):
    """Виджет для прохождения теста."""
    
    def __init__(self, scenario, user_name, user_surname, on_complete):
        super().__init__()
        self.scenario = scenario
        self.user_name = user_name
        self.user_surname = user_surname
        self.on_complete_callback = on_complete
        self.start_time = None
        self.question_widgets = []
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Информация о сценарии
        info_frame = QFrame()
        info_frame.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        info_layout = QVBoxLayout(info_frame)
        
        title_label = QLabel(f"Сценарий {self.scenario['id']}: {self.scenario['title']}")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        info_layout.addWidget(title_label)
        
        desc_label = QLabel(self.scenario['description'])
        desc_label.setWordWrap(True)
        info_layout.addWidget(desc_label)
        
        # Начальные данные
        initial_data = self.scenario.get('initial_data', {})
        if initial_data:
            data_text = " | ".join([f"{k}: {v}" for k, v in initial_data.items()])
            data_label = QLabel(f"<b>Условия сделки:</b> {data_text}")
            data_label.setStyleSheet("background-color: #e0e0ff; padding: 5px;")
            info_layout.addWidget(data_label)
        
        layout.addWidget(info_frame)
        
        # Таймер
        self.timer_label = QLabel("Время: 00:00")
        self.timer_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.timer_label.setStyleSheet("color: blue;")
        layout.addWidget(self.timer_label)
        
        # Scroll area для вопросов
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        self.questions_container = QWidget()
        self.questions_layout = QVBoxLayout(self.questions_container)
        
        self.create_question_widgets()
        
        scroll.setWidget(self.questions_container)
        layout.addWidget(scroll)
        
        # Кнопка завершения
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.finish_btn = QPushButton("Завершить тест")
        self.finish_btn.setFont(QFont("Arial", 12, QFont.Bold))
        self.finish_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 10px 20px;")
        self.finish_btn.clicked.connect(self.finish_test)
        btn_layout.addWidget(self.finish_btn)
        
        layout.addLayout(btn_layout)
        self.setLayout(layout)
    
    def create_question_widgets(self):
        """Создание виджетов для всех вопросов."""
        questions = self.scenario.get('questions', [])
        
        for i, q_data in enumerate(questions):
            q_frame = QFrame()
            q_frame.setFrameStyle(QFrame.Box | QFrame.Raised)
            q_layout = QVBoxLayout(q_frame)
            
            # Номер вопроса
            q_num_label = QLabel(f"Вопрос {i + 1}")
            q_num_label.setFont(QFont("Arial", 11, QFont.Bold))
            q_layout.addWidget(q_num_label)
            
            # Виджет вопроса в зависимости от типа
            q_type = q_data.get('type', 'single_choice')
            
            if q_type == 'single_choice':
                q_widget = SingleChoiceWidget(q_data)
            elif q_type == 'multiple_choice':
                q_widget = MultipleChoiceWidget(q_data)
            elif q_type == 'true_false':
                q_widget = TrueFalseWidget(q_data)
            elif q_type == 'ordering':
                q_widget = OrderingWidget(q_data)
            else:
                q_widget = SingleChoiceWidget(q_data)
            
            self.question_widgets.append(q_widget)
            q_layout.addWidget(q_widget)
            
            self.questions_layout.addWidget(q_frame)
    
    def start_timer(self):
        """Запуск таймера."""
        self.start_time = QTime.currentTime()
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)
        self.timer.start(1000)
    
    def update_timer(self):
        """Обновление таймера."""
        elapsed = QTime(0, 0).secsTo(QTime.currentTime().secsTo(self.start_time) * -1 if QTime.currentTime() < self.start_time else QTime.currentTime().secsTo(self.start_time))
        current = QTime(0, 0).addSecs(elapsed)
        self.timer_label.setText(f"Время: {current.toString('mm:ss')}")
    
    def get_elapsed_seconds(self):
        """Получить прошедшее время в секундах."""
        if self.start_time:
            return QTime(0, 0).secsTo(QTime.currentTime()) - QTime(0, 0).secsTo(self.start_time)
        return 0
    
    def finish_test(self):
        """Завершение теста и проверка ответов."""
        self.timer.stop()
        elapsed_seconds = self.get_elapsed_seconds()
        
        results = {
            'surname': self.user_surname,
            'name': self.user_name,
            'scenario_id': self.scenario['id'],
            'scenario_title': self.scenario['title'],
            'start_time': self.start_time.toString('HH:mm:ss'),
            'elapsed_seconds': elapsed_seconds,
            'total_questions': len(self.question_widgets),
            'correct_count': 0,
            'incorrect_count': 0,
            'question_results': []
        }
        
        questions = self.scenario.get('questions', [])
        
        for i, q_widget in enumerate(self.question_widgets):
            q_data = questions[i]
            user_answer = q_widget.get_answer()
            correct_answer = q_data.get('correct_answer', [])
            
            # Нормализация ответов для сравнения
            if isinstance(correct_answer, bool):
                is_correct = (user_answer == correct_answer)
            elif isinstance(correct_answer, list):
                # Для ordering сравниваем списки
                if q_data.get('type') == 'ordering':
                    is_correct = (sorted(user_answer or []) == sorted(correct_answer))
                else:
                    is_correct = (sorted(user_answer or []) == sorted(correct_answer))
            else:
                is_correct = (user_answer == correct_answer)
            
            q_result = {
                'question_id': q_data.get('id', f'q{i+1}'),
                'question_text': q_data['question'],
                'question_type': q_data.get('type', 'single_choice'),
                'user_answer': user_answer,
                'correct_answer': correct_answer,
                'is_correct': is_correct,
                'explanation': q_data.get('explanation', '')
            }
            
            results['question_results'].append(q_result)
            
            if is_correct:
                results['correct_count'] += 1
            else:
                results['incorrect_count'] += 1
        
        results['end_time'] = QTime.currentTime().toString('HH:mm:ss')
        results['date'] = datetime.now().strftime('%Y-%m-%d')
        
        self.on_complete_callback(results)


class ResultsDialog(QDialog):
    """Диалог отображения результатов теста."""
    
    def __init__(self, results, reglament_data, parent=None):
        super().__init__(parent)
        self.results = results
        self.reglament_data = reglament_data
        self.setWindowTitle("Результаты тестирования")
        self.setMinimumSize(800, 600)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Заголовок
        title_label = QLabel(f"Результаты: {self.results['surname']} {self.results['name']}")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(title_label)
        
        # Информация о тесте
        info_layout = QHBoxLayout()
        info_layout.addWidget(QLabel(f"Сценарий: {self.results['scenario_id']}"))
        info_layout.addWidget(QLabel(f"Дата: {self.results['date']}"))
        info_layout.addWidget(QLabel(f"Время начала: {self.results['start_time']}"))
        info_layout.addWidget(QLabel(f"Время окончания: {self.results['end_time']}"))
        elapsed_min = self.results['elapsed_seconds'] // 60
        elapsed_sec = self.results['elapsed_seconds'] % 60
        info_layout.addWidget(QLabel(f"Затраченное время: {elapsed_min}:{elapsed_sec:02d}"))
        layout.addLayout(info_layout)
        
        # Общий результат
        total = self.results['total_questions']
        correct = self.results['correct_count']
        percentage = (correct / total * 100) if total > 0 else 0
        
        result_label = QLabel(f"Правильных ответов: {correct} из {total} ({percentage:.1f}%)")
        result_label.setFont(QFont("Arial", 14, QFont.Bold))
        if percentage >= 80:
            result_label.setStyleSheet("color: green;")
        elif percentage >= 60:
            result_label.setStyleSheet("color: orange;")
        else:
            result_label.setStyleSheet("color: red;")
        layout.addWidget(result_label)
        
        # Детализация по вопросам
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        details_widget = QWidget()
        details_layout = QVBoxLayout(details_widget)
        
        for i, q_result in enumerate(self.results['question_results']):
            q_frame = QFrame()
            if q_result['is_correct']:
                q_frame.setStyleSheet("background-color: #e8f5e9; border: 1px solid green;")
            else:
                q_frame.setStyleSheet("background-color: #ffebee; border: 1px solid red;")
            
            q_layout = QVBoxLayout(q_frame)
            
            # Вопрос
            q_text = QLabel(f"{i+1}. {q_result['question_text']}")
            q_text.setFont(QFont("Arial", 11, QFont.Bold))
            q_text.setWordWrap(True)
            q_layout.addWidget(q_text)
            
            # Статус
            status = "✓ ПРАВИЛЬНО" if q_result['is_correct'] else "✗ ОШИБКА"
            status_label = QLabel(status)
            status_label.setFont(QFont("Arial", 10, QFont.Bold))
            q_layout.addWidget(status_label)
            
            # Объяснение
            expl_label = QLabel(f"Объяснение: {q_result['explanation']}")
            expl_label.setWordWrap(True)
            expl_label.setStyleSheet("color: #333; padding: 5px;")
            q_layout.addWidget(expl_label)
            
            details_layout.addWidget(q_frame)
        
        scroll.setWidget(details_widget)
        layout.addWidget(scroll)
        
        # Кнопки
        btn_layout = QHBoxLayout()
        
        self.export_pdf_btn = QPushButton("Экспорт в PDF")
        self.export_pdf_btn.clicked.connect(self.export_to_pdf)
        btn_layout.addWidget(self.export_pdf_btn)
        
        self.go_to_reglament_btn = QPushButton("Перейти к регламенту")
        self.go_to_reglament_btn.clicked.connect(self.go_to_reglament)
        btn_layout.addWidget(self.go_to_reglament_btn)
        
        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(close_btn)
        
        layout.addLayout(btn_layout)
        self.setLayout(layout)
    
    def export_to_pdf(self):
        """Экспорт результатов в PDF."""
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
        from reportlab.lib.units import cm
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib import colors
        
        filename = f"result_{self.results['surname']}_{self.results['scenario_id']}_{self.results['date']}.pdf"
        filepath = os.path.join(BASE_DIR, filename)
        
        doc = SimpleDocTemplate(filepath, pagesize=A4,
                                rightMargin=2*cm, leftMargin=2*cm,
                                topMargin=2*cm, bottomMargin=2*cm)
        
        elements = []
        styles = getSampleStyleSheet()
        
        # Заголовок
        title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=16, alignment=1)
        elements.append(Paragraph("Результаты тестирования", title_style))
        elements.append(Spacer(1, 0.5*cm))
        
        # Информация о тестируемом
        info_style = ParagraphStyle('Info', parent=styles['Normal'], fontSize=11)
        elements.append(Paragraph(f"<b>ФИО:</b> {self.results['surname']} {self.results['name']}", info_style))
        elements.append(Paragraph(f"<b>Сценарий:</b> {self.results['scenario_id']} - {self.results['scenario_title']}", info_style))
        elements.append(Paragraph(f"<b>Дата:</b> {self.results['date']}", info_style))
        elements.append(Paragraph(f"<b>Время начала:</b> {self.results['start_time']}", info_style))
        elements.append(Paragraph(f"<b>Время окончания:</b> {self.results['end_time']}", info_style))
        
        elapsed_min = self.results['elapsed_seconds'] // 60
        elapsed_sec = self.results['elapsed_seconds'] % 60
        elements.append(Paragraph(f"<b>Затраченное время:</b> {elapsed_min} мин. {elapsed_sec} сек.", info_style))
        elements.append(Spacer(1, 0.5*cm))
        
        # Общий результат
        total = self.results['total_questions']
        correct = self.results['correct_count']
        percentage = (correct / total * 100) if total > 0 else 0
        
        result_text = f"<b>Результат:</b> {correct} из {total} правильных ответов ({percentage:.1f}%)"
        elements.append(Paragraph(result_text, info_style))
        elements.append(Spacer(1, 0.5*cm))
        
        # Таблица с детализацией
        table_data = [['№', 'Вопрос', 'Статус', 'Объяснение']]
        
        for i, q_result in enumerate(self.results['question_results']):
            status = "Правильно" if q_result['is_correct'] else "Ошибка"
            # Обрезаем длинный текст вопроса
            q_text = q_result['question_text'][:80] + "..." if len(q_result['question_text']) > 80 else q_result['question_text']
            expl = q_result['explanation'][:100] + "..." if len(q_result['explanation']) > 100 else q_result['explanation']
            table_data.append([str(i+1), q_text, status, expl])
        
        table = Table(table_data, colWidths=[0.5*cm, 5*cm, 2*cm, 7*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
        ]))
        
        elements.append(table)
        
        doc.build(elements)
        
        QMessageBox.information(self, "Экспорт", f"Результаты сохранены в файл:\n{filepath}")
    
    def go_to_reglament(self):
        """Переход к регламенту (сигнал главному окну)."""
        # Главное окно обработает этот сигнал
        self.accept()
        # Главное окно переключится на вкладку изучения


class TestDataWidget(QWidget):
    """Виджет таблицы результатов тестирования."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.results_data = []
        self.init_ui()
        self.load_results()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        title_label = QLabel("Результаты тестирования")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(title_label)
        
        # Таблица
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "Дата", "Время", "Фамилия", "Имя", "Сценарий", 
            "Правильно", "Неправильно", "Детали"
        ])
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        layout.addWidget(self.table)
        
        # Кнопки
        btn_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("Обновить")
        refresh_btn.clicked.connect(self.load_results)
        btn_layout.addWidget(refresh_btn)
        
        export_btn = QPushButton("Экспорт выбранного в PDF")
        export_btn.clicked.connect(self.export_selected)
        btn_layout.addWidget(export_btn)
        
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
    
    def load_results(self):
        """Загрузка результатов из файла."""
        if os.path.exists(RESULTS_FILE):
            self.results_data = load_json(RESULTS_FILE)
        else:
            self.results_data = []
        
        self.table.setRowCount(len(self.results_data))
        
        for row, result in enumerate(self.results_data):
            self.table.setItem(row, 0, QTableWidgetItem(result.get('date', '')))
            self.table.setItem(row, 1, QTableWidgetItem(result.get('start_time', '')))
            self.table.setItem(row, 2, QTableWidgetItem(result.get('surname', '')))
            self.table.setItem(row, 3, QTableWidgetItem(result.get('name', '')))
            self.table.setItem(row, 4, QTableWidgetItem(f"{result.get('scenario_id', '')}"))
            self.table.setItem(row, 5, QTableWidgetItem(str(result.get('correct_count', 0))))
            self.table.setItem(row, 6, QTableWidgetItem(str(result.get('incorrect_count', 0))))
            
            # Кнопка для просмотра деталей
            details_btn = QPushButton("Просмотр")
            details_btn.clicked.connect(lambda checked, r=row: self.show_details(r))
            self.table.setCellWidget(row, 7, details_btn)
    
    def show_details(self, row):
        """Показ деталей результата."""
        if row < len(self.results_data):
            result = self.results_data[row]
            reglament_data = load_json(REGLEMENT_FILE)
            dialog = ResultsDialog(result, reglament_data, self)
            dialog.exec_()
    
    def export_selected(self):
        """Экспорт выбранной строки в PDF."""
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Предупреждение", "Выберите строку для экспорта")
            return
        
        row = selected_rows[0].row()
        result = self.results_data[row]
        reglament_data = load_json(REGLEMENT_FILE)
        
        dialog = ResultsDialog(result, reglament_data, self)
        dialog.export_to_pdf()


class TestingSetupWidget(QWidget):
    """Виджет настройки тестирования."""
    
    def __init__(self, scenarios, on_start_test):
        super().__init__()
        self.scenarios = scenarios
        self.on_start_test_callback = on_start_test
        self.init_ui()
        self.load_user_data()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        title_label = QLabel("Настройка тестирования")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(title_label)
        
        # Форма ввода данных
        form_layout = QFormLayout()
        
        # Фамилия
        self.surname_input = QLineEdit()
        self.surname_input.setPlaceholderText("Введите фамилию")
        form_layout.addRow("Фамилия:", self.surname_input)
        
        # Имя
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Введите имя")
        form_layout.addRow("Имя:", self.name_input)
        
        # Номер сценария
        scenario_layout = QHBoxLayout()
        
        self.scenario_combo = QComboBox()
        self.scenario_combo.addItem("-- Выберите сценарий --", None)
        
        # Стандартные тесты (1-20)
        self.scenario_combo.addItem("=== Стандартные тесты (1-20) ===", None)
        for i in range(1, 21):
            scenario_id = f"S{i:02d}"
            scenario = next((s for s in self.scenarios if s['id'] == scenario_id), None)
            if scenario:
                self.scenario_combo.addItem(f"{scenario_id}: {scenario['title'][:50]}...", scenario)
        
        # Углубленные тесты (21-40)
        self.scenario_combo.addItem("=== Углубленные тесты (21-40) ===", None)
        for i in range(21, 41):
            scenario_id = f"S{i:02d}"
            scenario = next((s for s in self.scenarios if s['id'] == scenario_id), None)
            if scenario:
                self.scenario_combo.addItem(f"{scenario_id}: {scenario['title'][:50]}...", scenario)
        
        scenario_layout.addWidget(self.scenario_combo)
        form_layout.addRow("Сценарий:", scenario_layout)
        
        # Подсказка
        hint_label = QLabel("Сценарии 1-20: стандартные тесты\nСценарии 21-40: углубленные тесты")
        hint_label.setStyleSheet("color: gray; font-style: italic;")
        form_layout.addRow("", hint_label)
        
        layout.addLayout(form_layout)
        layout.addStretch()
        
        # Кнопка начала теста
        self.start_btn = QPushButton("Начать тестирование")
        self.start_btn.setFont(QFont("Arial", 14, QFont.Bold))
        self.start_btn.setStyleSheet("background-color: #2196F3; color: white; padding: 15px 30px;")
        self.start_btn.clicked.connect(self.start_test)
        layout.addWidget(self.start_btn)
        
        self.setLayout(layout)
    
    def load_user_data(self):
        """Загрузка сохраненных данных пользователя."""
        if os.path.exists(USER_DATA_FILE):
            user_data = load_json(USER_DATA_FILE)
            self.surname_input.setText(user_data.get('surname', ''))
            self.name_input.setText(user_data.get('name', ''))
    
    def save_user_data(self):
        """Сохранение данных пользователя."""
        user_data = {
            'surname': self.surname_input.text(),
            'name': self.name_input.text()
        }
        save_json(USER_DATA_FILE, user_data)
    
    def start_test(self):
        """Начало тестирования."""
        surname = self.surname_input.text().strip()
        name = self.name_input.text().strip()
        
        if not surname or not name:
            QMessageBox.warning(self, "Предупреждение", "Введите фамилию и имя")
            return
        
        scenario = self.scenario_combo.currentData()
        if not scenario:
            QMessageBox.warning(self, "Предупреждение", "Выберите сценарий")
            return
        
        self.save_user_data()
        self.on_start_test_callback(scenario, surname, name)


class MainWindow(QMainWindow):
    """Главное окно приложения."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Система обучения и тестирования")
        self.setMinimumSize(1000, 700)
        
        # Загрузка данных
        self.reglament_data = load_json(REGLEMENT_FILE)
        self.scenarios_data = load_json(SCENARIOS_FILE)
        self.scenarios = self.scenarios_data.get('test_scenarios', [])
        
        self.init_ui()
    
    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        
        # Выбор режима
        mode_layout = QHBoxLayout()
        mode_label = QLabel("Режим работы:")
        mode_label.setFont(QFont("Arial", 12, QFont.Bold))
        mode_layout.addWidget(mode_label)
        
        self.mode_buttons = QButtonGroup(self)
        
        self.study_btn = QRadioButton("Изучение")
        self.study_btn.setFont(QFont("Arial", 12))
        self.study_btn.toggled.connect(lambda: self.switch_mode('study'))
        self.mode_buttons.addButton(self.study_btn, 0)
        mode_layout.addWidget(self.study_btn)
        
        self.test_btn = QRadioButton("Тестирование")
        self.test_btn.setFont(QFont("Arial", 12))
        self.test_btn.toggled.connect(lambda: self.switch_mode('test'))
        self.mode_buttons.addButton(self.test_btn, 1)
        mode_layout.addWidget(self.test_btn)
        
        self.results_view_btn = QRadioButton("Результаты")
        self.results_view_btn.setFont(QFont("Arial", 12))
        self.results_view_btn.toggled.connect(lambda: self.switch_mode('results'))
        self.mode_buttons.addButton(self.results_view_btn, 2)
        mode_layout.addWidget(self.results_view_btn)
        
        main_layout.addLayout(mode_layout)
        
        # Stacked widget для переключения режимов
        self.stacked_widget = QStackedWidget()
        
        # Виджет изучения
        self.reglament_viewer = ReglamentViewer()
        self.stacked_widget.addWidget(self.reglament_viewer)
        
        # Виджет настройки тестирования
        self.testing_setup = TestingSetupWidget(self.scenarios, self.start_test)
        self.stacked_widget.addWidget(self.testing_setup)
        
        # Виджет результатов
        self.results_widget = TestDataWidget()
        self.stacked_widget.addWidget(self.results_widget)
        
        # Контейнер для текущего теста
        self.test_container = QWidget()
        self.test_layout = QVBoxLayout(self.test_container)
        
        main_layout.addWidget(self.stacked_widget)
        
        self.setLayout(main_layout)
        
        # По умолчанию режим изучения
        self.study_btn.setChecked(True)
    
    def switch_mode(self, mode):
        """Переключение режима."""
        if mode == 'study':
            self.stacked_widget.setCurrentIndex(0)
        elif mode == 'test':
            self.stacked_widget.setCurrentIndex(1)
        elif mode == 'results':
            self.stacked_widget.setCurrentIndex(2)
            self.results_widget.load_results()
    
    def start_test(self, scenario, surname, name):
        """Запуск теста."""
        # Скрываем текущий виджет и показываем тест
        self.stacked_widget.setCurrentWidget(self.test_container)
        
        # Очищаем предыдущий тест
        while self.test_layout.count():
            item = self.test_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Создаем виджет теста
        self.test_widget = TestScenarioWidget(scenario, name, surname, self.on_test_complete)
        self.test_layout.addWidget(self.test_widget)
        
        # Запускаем таймер
        self.test_widget.start_timer()
    
    def on_test_complete(self, results):
        """Обработка завершения теста."""
        # Сохранение результатов
        if os.path.exists(RESULTS_FILE):
            all_results = load_json(RESULTS_FILE)
        else:
            all_results = []
        
        all_results.append(results)
        save_json(RESULTS_FILE, all_results)
        
        # Показ диалога результатов
        dialog = ResultsDialog(results, self.reglament_data, self)
        dialog.exec_()
        
        # Возврат к экрану настройки
        self.test_widget.deleteLater()
        self.stacked_widget.setCurrentWidget(self.testing_setup)


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Настройка шрифта
    font = QFont("Arial", 10)
    app.setFont(font)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
