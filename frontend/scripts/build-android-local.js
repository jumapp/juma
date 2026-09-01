#!/usr/bin/env node

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

// Colors for console output
const colors = {
  green: '\x1b[32m',
  red: '\x1b[31m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  magenta: '\x1b[35m',
  cyan: '\x1b[36m',
  reset: '\x1b[0m',
  bold: '\x1b[1m'
};

function log(message, color = 'reset') {
  console.log(`${colors[color] || ''} ${message} ${colors.reset}`);
}

function logError(message) {
  console.error(`${colors.red}❌ ${message}${colors.reset}`);
}

function logSuccess(message) {
  console.log(`${colors.green}✅ ${message}${colors.reset}`);
}

function logInfo(message) {
  console.log(`${colors.blue}ℹ️ ${message}${colors.reset}`);
}

function logStep(step, message) {
  console.log(`${colors.magenta}🔧 ${step}${colors.reset} ${message}`);
}

function getApkFiles(buildDirectory) {
  const apkFiles = [];
  const aabFiles = [];

  function scanDir(dir) {
    const items = fs.readdirSync(dir);
    for (const item of items) {
      const fullPath = path.join(dir, item);
      const stat = fs.statSync(fullPath);

      if (stat.isDirectory()) {
        scanDir(fullPath);
      } else if (stat.isFile()) {
        if (item.endsWith('.apk')) {
          apkFiles.push(fullPath);
        } else if (item.endsWith('.aab') || item.endsWith('.apkbundle')) {
          aabFiles.push(fullPath);
        }
      }
    }
  }

  if (fs.existsSync(buildDirectory)) {
    scanDir(buildDirectory);
  }

  return { apkFiles, aabFiles };
}

function runLint() {
  logStep('Linting', 'Running code quality checks...');
  try {
    execSync('npx expo lint --silent', { stdio: 'pipe' });
    logSuccess('Linting completed successfully');
    return true;
  } catch (error) {
    const output = error.stdout?.toString() || error.stderr?.toString() || '';
    logError('Linting failed');
    log('Lint output:', 'yellow');
    console.log(output);
    
    logInfo('Continue build despite lint errors? (y/N):');
    const rl = require('readline').createInterface({
      input: process.stdin,
      output: process.stdout
    });

    return new Promise(resolve => {
      rl.question('Continue build anyway? (y/N): ', (answer) => {
        rl.close();
        if (answer.toLowerCase() === 'y') {
          logInfo('Proceeding with build despite lint errors');
          resolve(true);
        } else {
          logError('Build cancelled by user');
          process.exit(1);
        }
      });
    });
  }
}

function checkPrerequisites() {
  logStep('Prerequisites', 'Checking build requirements...');

  const checks = [
    { name: 'Node.js', check: () => process.version },
    { name: 'npm', check: () => {
      try {
        execSync('npm --version', { stdio: 'pipe' });
        return true;
      } catch {
        return false;
      }
    }},
    { name: 'EXPO_TOKEN', check: () => process.env.EXPO_TOKEN },
    { name: 'Android SDK', check: () => {
      try {
        const androidHome = process.env.ANDROID_HOME || process.env.ANDROID_SDK_ROOT;
        if (!androidHome) return false;
        if (!fs.existsSync(androidHome)) return false;
        const platformsDir = path.join(androidHome, 'platforms');
        if (!fs.existsSync(platformsDir)) return false;
        return true;
      } catch {
        return false;
      }
    }},
    { name: 'Gradle wrapper', check: () => {
      const gradlewPath = path.join(process.cwd(), 'android', 'gradlew');
      return fs.existsSync(gradlewPath);
    }},
  ];

  const passed = [];
  const failed = [];

  for (const check of checks) {
    try {
      const result = check.check();
      if (result) {
        passed.push(check.name);
        logSuccess(`${check.name} ✓`);
      } else {
        failed.push(check.name);
        logError(`${check.name} ✗`);
      }
    } catch (error) {
      failed.push(check.name);
      logError(`${check.name} ✗ (${error.message})`);
    }
  }

  if (failed.length > 0) {
    logError(`Prerequisites check failed: ${failed.join(', ')}`);
    logInfo('Please install missing dependencies and try again');
    logInfo('For Android SDK: https://developer.android.com/studio/projects/install-sdk');
    logInfo('For EXPO_TOKEN: https://expo.dev/accounts -> Access tokens');
  } else {
    logSuccess(`All prerequisites met: ${passed.join(', ')}`);
  }

  return failed.length === 0;
}

function getProfileFromArgs() {
  const args = process.argv.slice(2);
  const profileIndex = args.indexOf('--profile');

  if (profileIndex !== -1 && profileIndex + 1 < args.length) {
    return args[profileIndex + 1];
  }

  return 'development';
}

function getOutputDirFromArgs() {
  const args = process.argv.slice(2);
  const outputIndex = args.indexOf('--output-dir');

  if (outputIndex !== -1 && outputIndex + 1 < args.length) {
    return args[outputIndex + 1];
  }

  return null;
}

function main() {
  const profile = getProfileFromArgs();
  const outputDir = getOutputDirFromArgs();
  const quiet = process.argv.includes('--quiet');

  logStep('Local Android Build', `Building for profile: ${profile}`);
  logInfo(`Output directory: ${outputDir || 'default (build-output)'}`);
  logInfo(`Quiet mode: ${quiet ? 'enabled' : 'disabled'}`);

  if (!quiet) {
    console.log();
  }

  const projectRoot = path.join(__dirname, '..');
  const buildDirectory = outputDir || path.join(projectRoot, 'build-output');

  if (!fs.existsSync(buildDirectory)) {
    fs.mkdirSync(buildDirectory, { recursive: true });
    logInfo(`Created output directory: ${buildDirectory}`);
  }

  const validProfiles = ['development', 'preview', 'staging', 'production'];

  if (!validProfiles.includes(profile)) {
    logError(`Invalid profile: ${profile}`);
    logInfo(`Valid profiles: ${validProfiles.join(', ')}`);
    process.exit(1);
  }

  if (!quiet) {
    console.log();
  }

  if (!checkPrerequisites()) {
    process.exit(1);
  }

  if (!quiet) {
    console.log();
  }

  logStep('Code Quality', 'Running lint checks before build...');

  try {
    runLint();
  } catch (error) {
    logError(`Linting failed: ${error.message}`);
    process.exit(1);
  }

  logStep('Build Process', `Building Android app (${profile}) using EAS...`);

  if (!quiet) {
    console.log();
  }

  const env = {
    ...process.env,
    EXPO_PUBLIC_API_URL: process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8000',
    EXPO_PUBLIC_API_URL_MOBILE: process.env.EXPO_PUBLIC_API_URL_MOBILE || 'http://localhost:8000',
  };

  try {
    execSync(
      `npx eas-cli@latest build -p android --profile ${profile} --non-interactive`,
      {
        stdio: quiet ? 'pipe' : 'inherit',
        env,
        cwd: projectRoot,
      }
    );

    logSuccess('EAS build completed successfully');

    const { apkFiles, aabFiles } = getApkFiles(buildDirectory);

    if (!quiet) {
      console.log();
    }

    logStep('Build Outputs', 'Finding and listing generated APKs...');

    if (apkFiles.length > 0) {
      logSuccess(`Found ${apkFiles.length} APK file(s):`);
      apkFiles.forEach(apk => {
        const stats = fs.statSync(apk);
        const sizeKB = Math.round(stats.size / 1024);
        logInfo(`  ${path.basename(apk)} - ${sizeKB} KB`);
      });
    } else {
      logError('No APK files found in build output');
      logInfo('APK files should be in:', buildDirectory);
      logInfo('Search for files matching: *.apk');
    }

    if (aabFiles.length > 0) {
      logSuccess(`Found ${aabFiles.length} AAB file(s):`);
      aabFiles.forEach(aab => {
        const stats = fs.statSync(aab);
        const sizeKB = Math.round(stats.size / 1024);
        logInfo(`  ${path.basename(aab)} - ${sizeKB} KB (App Bundle)`);
      });
    }

    logSuccess('Build process completed successfully!');

    logInfo('\nNext steps:');
    logInfo('1. Install the APK on your device/emulator using adb:');
    logInfo('   adb install path/to/apk.apk');
    logInfo('2. For development builds, you can also run:');
    logInfo('   npx expo run:android --device');
    logInfo('3. For more options, check the README.md documentation');

    if (!quiet) {
      console.log();
    }

  } catch (error) {
    logError('EAS build failed');
    console.error(error.message);
    process.exit(1);
  }
}

if (require.main === module) {
  main();
}

module.exports = { main, getApkFiles, runLint, checkPrerequisites };