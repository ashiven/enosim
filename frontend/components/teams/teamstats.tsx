import TeamCard from "@/components/teams/teamcard"

export default function TeamStats() {
   return (
      <div className="container mx-auto mt-12 mb-8">
         <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <TeamCard
               TeamName="Kleinmazama"
               TeamId="2"
               TeamSubnet="10.1.2.0"
               TeamAddress="10.1.2.1"
               TeamExperience="Noob"
            />
            <TeamCard
               TeamName="Karibu"
               TeamId="1"
               TeamSubnet="10.1.1.0"
               TeamAddress="10.1.1.1"
               TeamExperience="Noob"
            />
         </div>
      </div>
   )
}
