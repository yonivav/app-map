// App map screenshots for a React Native app on the iOS simulator: copy this file, change the
// steps, and run `app-map shots react-native ios <app dir> <map> <this file> <out>`. It runs as
// an XCUITest with the iOS adapter's AppMapShots; each snap also asks the app's JS helper, through
// the relay, where the map's components are.
import XCTest
import ObjectiveC

/// React Native apps keep animating; XCUITest would wait 60 s for an idle app on every tap.
private func skipIdleWaits() {
    guard let cls = NSClassFromString("XCUIApplicationProcess") else { return }
    let one: @convention(block) (AnyObject, Bool) -> Void = { _, _ in }
    let two: @convention(block) (AnyObject, Bool, Bool) -> Void = { _, _, _ in }
    if let method = class_getInstanceMethod(cls, NSSelectorFromString("waitForQuiescenceIncludingAnimationsIdle:")) {
        method_setImplementation(method, imp_implementationWithBlock(one))
    }
    if let method = class_getInstanceMethod(cls, NSSelectorFromString("waitForQuiescenceIncludingAnimationsIdle:isPreEvent:")) {
        method_setImplementation(method, imp_implementationWithBlock(two))
    }
}

final class AppMapScenario: XCTestCase {
    /// An Expo development build opens its launcher: its deep link (the `exp+<slug>` scheme in
    /// ios/<App>/Info.plist) goes straight to Metro. The first launch then opens the developer
    /// menu as a sheet, closed by its "xmark" button. A bare React Native app skips all this.
    private func openExpoDevBuild(_ shots: AppMapShots, scheme: String, firstScreenText: String) {
        shots.open("\(scheme)://expo-development-client/?url=http%3A%2F%2Flocalhost%3A8081")
        try? shots.tap("Open", timeout: 3)
        _ = shots.app.staticTexts[firstScreenText].waitForExistence(timeout: 120)
        if shots.app.buttons["Go home"].waitForExistence(timeout: 10) {
            try? shots.tap("xmark", timeout: 3)
            shots.wait(2)
        }
    }

    func testAppMap() {
        continueAfterFailure = true
        skipIdleWaits()
        let shots = AppMapShots()
        shots.app.launch()
        shots.wait(5)
        openExpoDevBuild(shots, scheme: "exp+myapp", firstScreenText: "Log In")
        shots.describe("first")  // the element tree, to find labels and identifiers to tap
        shots.step("login") { shots.snap("login_01_login") }
        shots.step("home") {
            try shots.tap("Sign in")  // a label, or a testID (its accessibility identifier)
            shots.wait(2)
            shots.snap("home_01_feed")
        }
        shots.report()
    }
}
