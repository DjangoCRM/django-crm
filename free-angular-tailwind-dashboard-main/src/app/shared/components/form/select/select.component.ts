import { CommonModule } from '@angular/common';
import { Component, Input, Output, EventEmitter, OnInit } from '@angular/core';

export interface Option {
  value: string;
  label: string;
}

@Component({
  selector: 'app-select',
  imports:[CommonModule],
  templateUrl: './select.component.html',
})
export class SelectComponent implements OnInit {
  @Input() options: Option[] = [];
  @Input() placeholder: string = 'Select an option';
  @Input() className: string = '';
  @Input() defaultValue: string = '';
  @Input() value: string = '';

  @Output() valueChange = new EventEmitter<string>();

  ngOnInit() {
    if (!this.value && this.defaultValue) {
      this.value = this.defaultValue;
    }
  }

  onChange(event: Event) {
    const value = (event.target as HTMLSelectElement).value;
    this.value = value;
    this.valueChange.emit(value);
  }
}