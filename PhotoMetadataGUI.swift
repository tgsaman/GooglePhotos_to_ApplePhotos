import SwiftUI

struct ContentView: View {
    @State private var rootPath: String = ""
    @State private var outputPath: String = ""
    @State private var dryRun: Bool = false
    @State private var workers: Int = 4
    @State private var statusMessage: String = ""
    @State private var running: Bool = false

    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text("Google Photos Metadata Patcher")
                .font(.title2)
                .bold()

            Form {
                HStack {
                    TextField("Export Folder", text: $rootPath)
                    Button("Browse") { chooseRoot() }
                }
                HStack {
                    TextField("Output CSV (optional)", text: $outputPath)
                    Button("Save As") { chooseOutput() }
                }
                Toggle("Dry Run", isOn: $dryRun)
                HStack {
                    Text("Workers")
                    Stepper(value: $workers, in: 1...16) {
                        Text("\(workers)")
                    }
                }
                Button("Run") { runProcess() }
                    .disabled(running || rootPath.isEmpty)
            }
            if !statusMessage.isEmpty {
                Text(statusMessage)
                    .font(.footnote)
                    .foregroundColor(.secondary)
            }
        }
        .padding(20)
        .frame(width: 450)
    }

    private func chooseRoot() {
        let panel = NSOpenPanel()
        panel.canChooseDirectories = true
        panel.canChooseFiles = false
        if panel.runModal() == .OK {
            rootPath = panel.url?.path ?? ""
        }
    }

    private func chooseOutput() {
        let panel = NSSavePanel()
        panel.allowedFileTypes = ["csv"]
        if panel.runModal() == .OK {
            outputPath = panel.url?.path ?? ""
        }
    }

    private func runProcess() {
        running = true
        statusMessage = "Running..."

        let script = Bundle.main.resourceURL!
            .appendingPathComponent("photo_metadata_patch.py").path

        var args = [script, rootPath, "--workers", "\(workers)"]
        if dryRun { args.append("--dry-run") }
        if !outputPath.isEmpty { args += ["--output", outputPath] }

        DispatchQueue.global().async {
            let task = Process()
            task.executableURL = URL(fileURLWithPath: "/usr/bin/env")
            task.arguments = ["python3"] + args

            let pipe = Pipe()
            task.standardOutput = pipe
            task.standardError = pipe

            do {
                try task.run()
                task.waitUntilExit()
                let data = pipe.fileHandleForReading.readDataToEndOfFile()
                let output = String(data: data, encoding: .utf8) ?? ""
                DispatchQueue.main.async {
                    self.statusMessage = output.isEmpty ? "Done" : output
                    self.running = false
                }
            } catch {
                DispatchQueue.main.async {
                    self.statusMessage = "Failed to run script: \(error.localizedDescription)"
                    self.running = false
                }
            }
        }
    }
}

@main
struct PhotoMetadataApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
        }
        .windowStyle(.titleBar)
    }
}
