import { test, expect } from '@playwright/test';

test.describe('VideoZone User Journeys', () => {

    test('Journey 1: The First Jump (Load & Feed)', async ({ page }) => {
        // 1. Start: User opens the application
        await page.goto('http://localhost:5173');

        // 2. Observation: See title and status
        await expect(page.getByText('VIDEOZONE')).toBeVisible();
        await expect(page.getByText('SYSTEM: ONLINE')).toBeVisible();

        // 3. Experience: Video feed is present
        const video = page.locator('img[alt="Live Hallucination Feed"]');
        await expect(video).toBeVisible();

        // Check if the stream is actually loading (src attribute points to backend)
        await expect(video).toHaveAttribute('src', 'http://localhost:8000/video_feed');
    });

    test('Journey 2: The Neural Override (Prompt Injection)', async ({ page }) => {
        await page.goto('http://localhost:5173');

        // 1. Context: Command Center is visible
        const input = page.getByPlaceholder('Inject dream parameters...');
        await expect(input).toBeVisible();

        // 2. Action: User types prompt
        const newPrompt = 'Underwater bioluminescent forest';
        await input.fill(newPrompt);

        // 3. Action: User clicks INJECT
        // We intercept the network request to verify it's sent correctly
        const requestPromise = page.waitForRequest(request =>
            request.url().includes('/update_prompt') && request.method() === 'POST'
        );

        await page.getByText('INJECT').click();

        const request = await requestPromise;
        expect(request.url()).toContain(`prompt=${encodeURIComponent(newPrompt)}`);
    });

});
