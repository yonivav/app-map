package appmap

import androidx.test.ext.junit.rules.ActivityScenarioRule
import androidx.test.platform.app.InstrumentationRegistry
import androidx.test.uiautomator.By
import androidx.test.uiautomator.UiDevice
import androidx.test.uiautomator.Until
import org.junit.Rule
import org.junit.Test

/**
 * A React Native app's screenshot scenario (Android). Run it with
 * `app-map shots react-native android <app dir> <map> <this file> <out>`.
 * Taps go through UiAutomator (texts, `accessibilityLabel` as the description, `testID` as the
 * resource id); each snap gets the components' rects from the app itself, through the relay.
 */
class AppMapScenario {
    @get:Rule
    val activity = ActivityScenarioRule(com.example.app.MainActivity::class.java)  // ← the app's MainActivity

    private val device = UiDevice.getInstance(InstrumentationRegistry.getInstrumentation())
    private val shots = AppMapShots(emptyList())  // the map's classes come from the relay

    private fun tap(text: String) {
        (device.wait(Until.findObject(By.text(text)), 30_000) ?: throw AssertionError("no \"$text\"")).click()
        Thread.sleep(2500)
    }

    /** An Expo development build opens its launcher and, the first time, its developer menu. */
    private fun openExpoDevBuild(firstScreenText: String) {
        device.wait(Until.findObject(By.textContains(":8081")), 30_000)?.click()
        for (attempt in 0 until 3) {
            if (device.wait(Until.hasObject(By.text(firstScreenText)), 60_000)) break
            device.findObject(By.text("Continue"))?.click()
        }
        if (device.hasObject(By.text("Reload")) && device.hasObject(By.text("Go home"))) {
            device.pressBack()
            Thread.sleep(1500)
        }
    }

    @Test
    fun appMap() {
        openExpoDevBuild("Sign in")  // ← a text on the app's first screen
        shots.step("login") { shots.snap("login_01_login") }
        shots.step("home") {
            tap("Sign in")
            shots.snap("home_01_feed")
        }
        shots.report()
    }
}
