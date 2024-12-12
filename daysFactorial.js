// Seleccionar todas las filas de la tabla
const rows = document.querySelectorAll('tr');

// Crear un objeto para almacenar los datos
const employeeDays = {};

// Recorrer cada fila
rows.forEach(row => {
  // Intentar obtener el nombre del empleado desde el segundo div dentro de un <a>
  const employeeCell = row.querySelector('th a div:nth-child(2), td a div:nth-child(2)');
  
  if (employeeCell) {
    const employeeName = employeeCell.textContent.trim();

    // Buscar todos los divs dentro de un div con role="tooltip" dentro de la fila
    const tooltipDivs = row.querySelectorAll('div[role="tooltip"] div');

    // Contar los divs con el color de fondo 'rgb(81, 81, 100)'
    const matchingDivsCount = Array.from(tooltipDivs).filter(div => {
      const bgColor = window.getComputedStyle(div).getPropertyValue('background-color');
      return bgColor === 'rgb(81, 81, 100)';
    }).length;

    // Agregar el conteo al objeto (sumar si ya existe el empleado)
    employeeDays[employeeName] = (employeeDays[employeeName] || 0) + matchingDivsCount;
  }
});

// Convertir el objeto a un formato de texto
const resultText = Object.entries(employeeDays)
  .map(([name, count]) => `${name}: ${count} días`)
  .join('\n');

// Crear y descargar el archivo .txt
const blob = new Blob([resultText], { type: 'text/plain' });
const link = document.createElement('a');
link.href = URL.createObjectURL(blob);
link.download = 'empleados_dias.txt';
document.body.appendChild(link);
link.click();
document.body.removeChild(link);

console.log('Archivo generado con éxito:', resultText);
