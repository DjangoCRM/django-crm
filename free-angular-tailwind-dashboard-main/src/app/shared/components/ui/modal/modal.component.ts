import { CommonModule } from '@angular/common';
import {
  Component,
  Input,
  Output,
  EventEmitter,
  ElementRef,
  OnInit,
  OnDestroy,
  HostListener
} from '@angular/core';

@Component({
  selector: 'app-modal',
  imports: [
    CommonModule,
  ],
  templateUrl: './modal.component.html',
  styles: ``
})
export class ModalComponent {

  @Input() isOpen = false;
  @Output() close = new EventEmitter<void>();
  @Input() className = '';
  @Input() showCloseButton = true;
  @Input() isFullscreen = false;

  constructor(private el: ElementRef) {}

  ngOnInit() {
    if (this.isOpen) {
      document.body.style.overflow = 'hidden';
    }
  }

  ngOnDestroy() {
    document.body.style.overflow = 'unset';
  }

  ngOnChanges() {
    document.body.style.overflow = this.isOpen ? 'hidden' : 'unset';
  }

  onBackdropClick(event: MouseEvent) {
    if (!this.isFullscreen) {
      this.close.emit();
    }
  }

  onContentClick(event: MouseEvent) {
    event.stopPropagation();
  }

  @HostListener('document:keydown.escape', ['$event'])
  onEscape(event: KeyboardEvent) {
    if (this.isOpen) {
      this.close.emit();
    }
  }
}
