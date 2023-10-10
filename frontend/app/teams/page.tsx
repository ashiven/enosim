import TeamStats from "@/components/teamstats"

import Navbar from "@components/navbar"
import Sidebar from "@components/sidebar"

export default function Home() {
   return (
      <main>
         <Navbar />
         <div className="flex">
            <Sidebar />
            <div className="container">
               <TeamStats />
            </div>
         </div>
      </main>
   )
}
