import { Link, Outlet } from "react-router-dom";
import { APP_TITLE } from "../constants";
import { Sidebar } from "./Sidebar";
import { ThemeToggle } from "./ThemeToggle";

export function Layout() {
  return (
    <div className="flex min-h-full flex-col">
      <header className="flex items-center justify-between border-b px-6 py-3">
        <Link to="/" className="text-lg font-semibold">
          {APP_TITLE}
        </Link>
        <ThemeToggle />
      </header>
      <div className="flex flex-1 flex-col md:flex-row">
        <Sidebar />
        <main className="flex-1 p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
