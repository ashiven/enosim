import VMStats from "@/components/vmstats"

import Navbar from "@components/navbar"
import Sidebar from "@components/sidebar"

export default function Home() {
   return (
      <main className="">
         <Navbar />
         <div className="flex">
            <Sidebar />
            <VMStats />
         </div>
      </main>
   )
}
