import VideoUpload from "./VideoUpload";

export default function Home() {
  return (
    <main className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-blue-100 to-teal-100 p-4">
      <div className="w-full max-w-2xl">
        <div className="mb-8">
          <h1 className="text-4xl font-extrabold text-center mb-2 text-blue-900 drop-shadow">Marine Life Detection</h1>
          <p className="text-center text-gray-700 text-lg">Upload a video to detect marine life using AI.</p>
        </div>
        {/* Video Upload Component */}
        <div className="mb-8">
          <VideoUpload />
        </div>
        <footer className="text-center text-xs text-gray-500 mt-8">
          &copy; {new Date().getFullYear()} Marine Life Detection App
        </footer>
      </div>
    </main>
  );
}
