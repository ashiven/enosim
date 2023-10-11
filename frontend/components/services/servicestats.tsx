import ServiceCard from "@/components/services/servicecard"

export default function ServiceStats() {
   return (
      <div className="container mx-auto mt-12 mb-8">
         <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <ServiceCard
               name="CVExchange"
               id={1}
               flagsPerRound={1}
               noisesPerRound={1}
               havocsPerRound={2}
               weightFactor={1}
               github="https://github.com/enowars/enowars7-service-CVExchange"
            />
            <ServiceCard
               name="bollwerk"
               id={2}
               flagsPerRound={1}
               noisesPerRound={1}
               havocsPerRound={2}
               weightFactor={1}
               github="https://github.com/enowars/enowars7-service-bollwerk"
            />
         </div>
      </div>
   )
}
