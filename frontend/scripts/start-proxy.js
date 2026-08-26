const { exec } = require('child_process');
const fs = require('fs');
const path = require('path');

// Path to .env file
const envPath = path.join(__dirname, '..', '.env');

// Read current .env content
let envContent = '';
try {
  envContent = fs.readFileSync(envPath, 'utf8');
} catch (err) {
  console.error('Error reading .env file:', err.message);
  console.log('Creating new .env file from .env.example...');
  const examplePath = path.join(__dirname, '..', '.env.example');
  if (fs.existsSync(examplePath)) {
    fs.copyFileSync(examplePath, envPath);
    envContent = fs.readFileSync(envPath, 'utf8');
  } else {
    envContent = '';
  }
}

// Start ngrok tunnel
console.log('🔗 Starting ngrok tunnel to localhost:8000...');

const ngrok = exec('ngrok http 8000 --log=stdout', (error, stdout, stderr) => {
  if (error) {
    console.error('Ngrok error:', error.message);
    console.log('\n💡 Make sure ngrok is installed and authenticated:');
    console.log('   1. Download from https://ngrok.com/download');
    console.log('   2. Run: ngrok config add-authtoken <YOUR_TOKEN>');
    return;
  }
});

// Parse ngrok output for the public URL
let ngrokUrl = null;
let urlFound = false;

ngrok.stdout.on('data', (data) => {
  const output = data.toString();
  
  // Look for the URL in ngrok output
  const urlMatch = output.match(/https?:\/\/[a-zA-Z0-9\-]+\.ngrok\.io/);
  if (urlMatch && !urlFound) {
    urlFound = true;
    ngrokUrl = urlMatch[0];
    
    console.log(`✅ Ngrok tunnel established: ${ngrokUrl}`);
    
    // Update .env file
    let newEnvContent = envContent.replace(
      /EXPO_PUBLIC_API_URL=.*/,
      `EXPO_PUBLIC_API_URL=${ngrokUrl}`
    );
    
    // If EXPO_PUBLIC_API_URL doesn't exist, add it
    if (!envContent.includes('EXPO_PUBLIC_API_URL=')) {
      newEnvContent = `EXPO_PUBLIC_API_URL=${ngrokUrl}\n${envContent}`;
    }
    
    fs.writeFileSync(envPath, newEnvContent);
    console.log(`📝 Updated ${envPath} with new API URL`);
    console.log('🚀 Ready to start Expo! Run: expo start');
  }
});

ngrok.stderr.on('data', (data) => {
  const output = data.toString();
  // Also check stderr for URL (ngrok sometimes outputs there)
  if (!urlFound) {
    const urlMatch = output.match(/https?:\/\/[a-zA-Z0-9\-]+\.ngrok\.io/);
    if (urlMatch) {
      urlFound = true;
      ngrokUrl = urlMatch[0];
      console.log(`✅ Ngrok tunnel established: ${ngrokUrl}`);
      
      let newEnvContent = envContent.replace(
        /EXPO_PUBLIC_API_URL=.*/,
        `EXPO_PUBLIC_API_URL=${ngrokUrl}`
      );
      
      if (!envContent.includes('EXPO_PUBLIC_API_URL=')) {
        newEnvContent = `EXPO_PUBLIC_API_URL=${ngrokUrl}\n${envContent}`;
      }
      
      fs.writeFileSync(envPath, newEnvContent);
      console.log(`📝 Updated ${envPath} with new API URL`);
      console.log('🚀 Ready to start Expo! Run: expo start');
    }
  }
});

ngrok.on('close', (code) => {
  if (code !== 0) {
    console.log(`Ngrok process exited with code ${code}`);
  }
});

// Handle graceful shutdown
process.on('SIGINT', () => {
  console.log('\n🛑 Shutting down ngrok...');
  ngrok.kill();
  process.exit();
});