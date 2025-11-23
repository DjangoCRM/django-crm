import { Component } from '@angular/core';
import { ComponentCardComponent } from '../../../common/component-card/component-card.component';
import { CardIconOneComponent } from '../card-icon-one/card-icon-one.component';
import { CardIconTwoComponent } from '../card-icon-two/card-icon-two.component';

@Component({
  selector: 'app-card-with-icon-example',
  imports: [
    ComponentCardComponent,
    CardIconOneComponent,
    CardIconTwoComponent,
],
  templateUrl: './card-with-icon-example.component.html',
  styles: ``
})
export class CardWithIconExampleComponent {

}
