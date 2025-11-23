import { Component } from '@angular/core';
import { ComponentCardComponent } from '../../../common/component-card/component-card.component';
import { CardFourComponent } from '../card-four/card-four.component';
import { CardFiveComponent } from '../card-five/card-five.component';

@Component({
  selector: 'app-horizontal-card-with-image',
  imports: [
    ComponentCardComponent,
    CardFourComponent,
    CardFiveComponent,
  ],
  templateUrl: './horizontal-card-with-image.component.html',
  styles: ``
})
export class HorizontalCardWithImageComponent {

}
