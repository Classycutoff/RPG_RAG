const { exec } = require('child_process');

exec('docker-compose up --build', (err, stdout, stderr) => {
  if (err) {
    console.error(`Error: ${stderr}`);
  } else {
    console.log(`Output: ${stdout}`);
  }
});