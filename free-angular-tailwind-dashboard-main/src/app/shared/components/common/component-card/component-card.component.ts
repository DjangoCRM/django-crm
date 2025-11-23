import { CommonModule } from '@angular/common';
import { Component, Input } from '@angular/core';

@Component({
  selector: 'app-component-card',
  imports: [CommonModule],
  templateUrl: './component-card.component.html',
  styles: ``
})
export class ComponentCardComponent {

  @Input() title!: string;
  @Input() desc: string = '';
  @Input() className: string = '';
}
