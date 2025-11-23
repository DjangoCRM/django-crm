import { Component } from '@angular/core';
import { CardComponent } from '../../../ui/card/card.component';
import { CardTitleComponent } from '../../../ui/card/card-title.component';
import { CardDescriptionComponent } from '../../../ui/card/card-description.component';
import { RouterModule } from '@angular/router';

@Component({
  selector: 'app-card-one',
  imports: [
    CardComponent,
    CardTitleComponent,
    CardDescriptionComponent,
    RouterModule,
  ],
  templateUrl: './card-one.component.html',
  styles: ``
})
export class CardOneComponent {

}
