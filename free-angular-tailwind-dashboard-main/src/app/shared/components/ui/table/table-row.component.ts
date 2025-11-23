import { CommonModule } from '@angular/common';
import { Component, Input } from '@angular/core';

@Component({
  selector: 'app-table-row',
  imports: [CommonModule],
  template: `
   <tr [ngClass]="className"><ng-content></ng-content></tr>
  `,
})
export class TableRowComponent {
  @Input() className = '';
}
