import { CommonModule } from '@angular/common';
import { Component, Input } from '@angular/core';

@Component({
  selector: 'app-table-body',
  imports: [CommonModule],
  template: `
    <tbody [ngClass]="className"><ng-content></ng-content></tbody>
  `,
})
export class TableBodyComponent {
  @Input() className = '';
}
