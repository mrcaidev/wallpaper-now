import {
  useLogInMutation,
  useLogOutMutation,
  useMeQuery,
} from "@/apis/user.ts";
import { Loader2Icon, LogInIcon, LogOutIcon, XIcon } from "lucide-react";
import { type FormEventHandler, useState } from "react";
import { Button } from "./ui/button.tsx";
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "./ui/dialog";
import { Input } from "./ui/input.tsx";
import { Label } from "./ui/label.tsx";
import { Skeleton } from "./ui/skeleton.tsx";

export function Header() {
  return (
    <header className="fixed inset-x-0 top-0 border-b bg-background/80 backdrop-blur-lg z-10">
      <div className="flex items-center justify-between max-w-7xl px-6 py-3 mx-auto">
        <span className="text-2xl font-[Rochester]">Wallpaper Now</span>
        <UserMenu />
      </div>
    </header>
  );
}

function UserMenu() {
  const { data: me, isPending } = useMeQuery();

  if (isPending) {
    return <Skeleton className="w-32 h-10" />;
  }

  if (!me) {
    return <LogInDialog />;
  }

  return (
    <div className="flex items-center gap-2">
      <span className="text-sm">{me.username}</span>
      <LogOutButton />
    </div>
  );
}

function LogInDialog() {
  const [open, setOpen] = useState(false);

  const { mutate, isPending } = useLogInMutation();

  const handleSubmit: FormEventHandler<HTMLFormElement> = (event) => {
    event.preventDefault();

    mutate(new FormData(event.currentTarget), {
      onSuccess: () => {
        setOpen(false);
      },
    });
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button>
          <LogInIcon />
          Log in
        </Button>
      </DialogTrigger>
      <DialogContent className="max-w-sm">
        <DialogHeader>
          <DialogTitle className="mb-3">Log In</DialogTitle>
          <DialogDescription>
            Welcome to Wallpaper Now! Log in to enjoy personalized
            recommendations and more.
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="grid gap-4" id="login-form">
          <div className="grid gap-2">
            <Label htmlFor="username">Username</Label>
            <Input type="text" name="username" required id="username" />
          </div>
          <div className="grid gap-2">
            <Label htmlFor="password">Password</Label>
            <Input type="password" name="password" required id="password" />
          </div>
        </form>
        <DialogFooter>
          <DialogClose asChild>
            <Button variant="secondary">
              <XIcon />
              Not now
            </Button>
          </DialogClose>
          <Button type="submit" form="login-form" disabled={isPending}>
            {isPending ? (
              <Loader2Icon className="animate-spin" />
            ) : (
              <LogInIcon />
            )}
            Log in
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

function LogOutButton() {
  const logOut = useLogOutMutation();

  return (
    <Button variant="ghost" size="icon" onClick={logOut} aria-label="Log out">
      <LogOutIcon />
    </Button>
  );
}
