import { Component } from '@angular/core';
import { ComponentCardComponent } from '../../../common/component-card/component-card.component';
import { CardLinkOneComponent } from '../card-link-one/card-link-one.component';
import { CardLinkTwoComponent } from '../card-link-two/card-link-two.component';
import { CardComponent } from "../../../ui/card/card.component";

@Component({
  selector: 'app-card-with-link-example',
  imports: [
    ComponentCardComponent,
    CardLinkOneComponent,
    CardLinkTwoComponent,
],
  templateUrl: './card-with-link-example.component.html',
  styles: ``
})
export class CardWithLinkExampleComponent {

}
