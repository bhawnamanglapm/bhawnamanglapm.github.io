// Amplitude analytics entry point.
//
// This file is bundled by `npm run build` into ../amplitude-init.js, which is
// committed and loaded by index.html with a plain <script> tag. GitHub Pages
// serves this repo as-is with no build step, so the bundle must be rebuilt and
// committed whenever this file or the SDK version changes.
//
// Runs client-side only — there is no server in this project.
import * as amplitude from '@amplitude/unified';

// Amplitude ingestion key — public by design; move to an env var when you set up environments.
const AMPLITUDE_API_KEY = '769a78a503e2c294acfcc18ff7de1ebe';

amplitude.initAll(AMPLITUDE_API_KEY, {"analytics":{"autocapture":true},"sessionReplay":{"sampleRate":1}});

amplitude.track('Viewed Home Page', { prompt_version: 'BA400.4' }); // helps improve this setup flow — safe to remove once you've verified the event lands
