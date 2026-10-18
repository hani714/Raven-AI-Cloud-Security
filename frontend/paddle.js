import { initializePaddle } from '@paddle/paddle-js';

const paddle = await initializePaddle({
  environment: 'production',
  token: 'test_eba79469ff7451d7681e585594d'
});