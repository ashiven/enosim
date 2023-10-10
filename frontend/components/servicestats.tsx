import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import {
   HoverCard,
   HoverCardContent,
   HoverCardTrigger,
} from "@/components/ui/hover-card"

export default function ServiceStats() {
   return (
      <div className="container mx-auto mt-12 mb-8">
         <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            {/* CVExchange card */}
            <HoverCard>
               <HoverCardTrigger>
                  <Card>
                     <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">
                           CVExchange
                        </CardTitle>
                        <svg
                           xmlns="http://www.w3.org/2000/svg"
                           viewBox="0 0 24 24"
                           fill="none"
                           stroke="currentColor"
                           strokeLinecap="round"
                           strokeLinejoin="round"
                           strokeWidth="2"
                           className="h-4 w-4 text-muted-foreground"
                        >
                           <path d="M22 12h-4l-3 9L9 3l-3 9H2" />
                        </svg>
                     </CardHeader>
                     <CardContent>
                        <div className="text-2xl font-bold">+573</div>
                     </CardContent>
                  </Card>
               </HoverCardTrigger>
               <HoverCardContent>
                  Flagstores: 3 - Flags per minute: 2
               </HoverCardContent>
            </HoverCard>
            {/* bollwerk card */}
            <HoverCard>
               <HoverCardTrigger>
                  <Card>
                     <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">
                           bollwerk
                        </CardTitle>
                        <svg
                           xmlns="http://www.w3.org/2000/svg"
                           viewBox="0 0 24 24"
                           fill="none"
                           stroke="currentColor"
                           strokeLinecap="round"
                           strokeLinejoin="round"
                           strokeWidth="2"
                           className="h-4 w-4 text-muted-foreground"
                        >
                           <path d="M22 12h-4l-3 9L9 3l-3 9H2" />
                        </svg>
                     </CardHeader>
                     <CardContent>
                        <div className="text-2xl font-bold">+573</div>
                     </CardContent>
                  </Card>
               </HoverCardTrigger>
               <HoverCardContent>
                  Flagstores: 2 - Flags per minute: 2
               </HoverCardContent>
            </HoverCard>
         </div>
      </div>
   )
}
