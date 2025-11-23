import { CommonModule } from '@angular/common';
import { Component, Input } from '@angular/core';

@Component({
  selector: 'app-aspect-ratio-video',
  imports: [
    CommonModule,
  ],
  templateUrl: './aspect-ratio-video.component.html',
  styles: ``
})
export class AspectRatioVideoComponent {

  @Input() videoUrl!: string;
  @Input() aspectRatio: string = 'video'; // Tailwind's aspect-ratio value like '16/9'
  @Input() title: string = 'Embedded Video';

  get aspectRatioClass(): string {
    return `aspect-${this.aspectRatio}`;
  }
}
