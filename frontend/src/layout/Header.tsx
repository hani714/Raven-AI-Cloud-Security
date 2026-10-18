export function Header() {
  return (
    <div className="flex items-center gap-3 px-2 py-3">
      <div className="relative">
        <img
          src="/raven.png"
          alt="Raven Logo"
          className="size-8 shrink-0 drop-shadow-[0_0_10px_hsl(var(--primary)/0.6)]"
        />
      </div>
      <div className="flex flex-col leading-tight">
        <span className="font-display text-base font-bold tracking-[0.3em] text-foreground">
          RAVEN
        </span>
      </div>
    </div>
  );
}

export default Header;
