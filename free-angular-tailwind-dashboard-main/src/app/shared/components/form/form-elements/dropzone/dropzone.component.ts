import { CommonModule } from '@angular/common';
import { Component, Output, EventEmitter, HostListener } from '@angular/core';
import { ComponentCardComponent } from '../../../common/component-card/component-card.component';


@Component({
  selector: 'app-dropzone',
  imports: [
    CommonModule,
    ComponentCardComponent,
  ],
  templateUrl: './dropzone.component.html',
  styles: ``
})
export class DropzoneComponent {

  isDragActive = false;

  @Output() filesDropped = new EventEmitter<File[]>();

  onFileSelected(event: Event) {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files.length) {
      this.filesDropped.emit(Array.from(input.files));
      console.log('Files dropped:', Array.from(input.files));
    }
  }

  @HostListener('dragover', ['$event'])
  onDragOver(event: DragEvent) {
    event.preventDefault();
    this.isDragActive = true;
  }

  @HostListener('dragleave', ['$event'])
  onDragLeave(event: DragEvent) {
    event.preventDefault();
    this.isDragActive = false;
  }

  @HostListener('drop', ['$event'])
  onDrop(event: DragEvent) {
    event.preventDefault();
    this.isDragActive = false;
    if (event.dataTransfer && event.dataTransfer.files.length) {
      const files = Array.from(event.dataTransfer.files).filter(file =>
        ['image/png', 'image/jpeg', 'image/webp', 'image/svg+xml'].includes(file.type)
      );
      this.filesDropped.emit(files);
      console.log('Files dropped:', files);
    }
  }
}
