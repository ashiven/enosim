import {
   Select,
   SelectContent,
   SelectItem,
   SelectTrigger,
   SelectValue,
} from "@/components/ui/select"

import Navbar from "@components/navbar"
import { Button } from "@components/ui/button"

export default function Home() {
   return (
      <main className="">
         <Navbar />
         <section>
            <ul>
               <li>
                  <Button>Hello World</Button>
               </li>
               <li>
                  <Button>Bye World</Button>
               </li>
            </ul>
         </section>
         <Select>
            <SelectTrigger className="w-[180px]">
               <SelectValue placeholder="Theme" />
            </SelectTrigger>
            <SelectContent>
               <SelectItem value="light">Light</SelectItem>
               <SelectItem value="dark">Dark</SelectItem>
               <SelectItem value="system">System</SelectItem>
            </SelectContent>
         </Select>
      </main>
   )
}
