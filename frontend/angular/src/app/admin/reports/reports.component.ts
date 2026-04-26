import { Component } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { ReportService } from '../../services/report.service';
import { saveAs } from 'file-saver';

@Component({
  selector: 'app-reports',
  templateUrl: './reports.component.html',
  styleUrls: ['./reports.component.css']
})
export class ReportsComponent {
  reportForm: FormGroup;
  loading = false;
  reportType = 'orders';

  constructor(
    private fb: FormBuilder,
    private reportService: ReportService
  ) {
    const today = new Date();
    const thirtyDaysAgo = new Date();
    thirtyDaysAgo.setDate(today.getDate() - 30);

    this.reportForm = this.fb.group({
      start_date: [thirtyDaysAgo.toISOString().split('T')[0], Validators.required],
      end_date: [today.toISOString().split('T')[0], Validators.required],
      include_kpis: [true],
      include_charts: [false]
    });
  }

  generateReport() {
    if (this.reportForm.invalid) {
      return;
    }

    this.loading = true;
    const filters = this.reportForm.value;

    if (this.reportType === 'orders') {
      this.reportService.generateOrdersReport(filters).subscribe({
        next: (blob) => {
          const filename = `reporte_pedidos_${new Date().toISOString().split('T')[0]}.pdf`;
          saveAs(blob, filename);
          this.loading = false;
          alert('Reporte generado exitosamente');
        },
        error: (error) => {
          console.error('Error generating report:', error);
          alert('Error al generar el reporte');
          this.loading = false;
        }
      });
    } else {
      this.reportService.generateExecutiveReport(filters).subscribe({
        next: (blob) => {
          const filename = `reporte_ejecutivo_${new Date().toISOString().split('T')[0]}.pdf`;
          saveAs(blob, filename);
          this.loading = false;
          alert('Reporte ejecutivo generado exitosamente');
        },
        error: (error) => {
          console.error('Error generating executive report:', error);
          alert('Error al generar el reporte ejecutivo');
          this.loading = false;
        }
      });
    }
  }
}