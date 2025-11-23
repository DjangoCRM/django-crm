import { Component } from '@angular/core';
import { RouterModule } from '@angular/router';
import { CardComponent } from '../../../ui/card/card.component';
import { CardTitleComponent } from '../../../ui/card/card-title.component';
import { CardDescriptionComponent } from '../../../ui/card/card-description.component';

@Component({
  selector: 'app-card-three',
  imports: [
    RouterModule,
    CardComponent,
    CardTitleComponent,
    CardDescriptionComponent,
  ],
  templateUrl: './card-three.component.html',
  styles: ``
})
export class CardThreeComponent {

}
