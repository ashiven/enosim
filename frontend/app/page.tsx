import {
   Select,
   SelectContent,
   SelectItem,
   SelectTrigger,
   SelectValue,
} from "@/components/ui/select"

import Navbar from "@components/navbar"
import Sidebar from "@components/sidebar"

export default function Home() {
   return (
      <main className="">
         <Navbar />
         <Sidebar />
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
