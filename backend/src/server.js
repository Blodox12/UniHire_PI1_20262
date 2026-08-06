const app = require('./app');
const { initialize } = require('./database/db');

const PORT = process.env.PORT || 5000;

initialize()
  .then(() => {
    app.listen(PORT, () => {
      console.log(`UniHire backend running on port ${PORT}`);
    });
  })
  .catch((error) => {
    console.error('Failed to initialize database', error);
    process.exit(1);
  });
