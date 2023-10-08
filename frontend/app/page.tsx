import { Button } from "@components/ui/button"
import { ModeToggle } from "@components/ui/toggle"

export default function Home() {
   return (
      <main className="">
         <Button>Hello World</Button>
         <Button>Bye World</Button>
         <ModeToggle />
      </main>
   )
}
