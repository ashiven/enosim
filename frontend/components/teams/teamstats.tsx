import TeamCard from "@/components/teams/teamcard"

export default function TeamStats() {
   return (
      <div className="container mx-auto mt-12 mb-8">
         <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <TeamCard
               name="Kleinmazama"
               id={2}
               subnet="10.1.2.0"
               address="10.1.2.1"
               experience="Noob"
               points={20000}
               gain={200}
            />
            <TeamCard
               name="Karibu"
               id={1}
               subnet="10.1.1.0"
               address="10.1.1.1"
               experience="Noob"
               points={20000}
               gain={200}
            />
         </div>
      </div>
   )
}
