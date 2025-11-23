import { Component } from '@angular/core';
import { SwitchComponent } from '../../input/switch.component';
import { ComponentCardComponent } from '../../../common/component-card/component-card.component';

@Component({
  selector: 'app-toggle-switch',
  imports: [
    SwitchComponent,
    ComponentCardComponent,
  ],
  templateUrl: './toggle-switch.component.html',
  styles: ``
})
export class ToggleSwitchComponent {

  handleSwitchChange(checked: boolean) {
    console.log('Switch is now:', checked ? 'ON' : 'OFF');
  }
}
