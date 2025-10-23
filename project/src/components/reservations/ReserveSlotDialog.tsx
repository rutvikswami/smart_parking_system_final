import { useState } from 'react'
import { motion } from 'framer-motion'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog'

interface ReserveSlotDialogProps {
  isOpen: boolean
  onClose: () => void
  onConfirm: (startTime: string, endTime: string) => void
  slotNumber: number
}

export function ReserveSlotDialog({
  isOpen,
  onClose,
  onConfirm,
  slotNumber,
}: ReserveSlotDialogProps) {
  const [startTime, setStartTime] = useState('')
  const [endTime, setEndTime] = useState('')

  const handleConfirm = () => {
    if (startTime && endTime) {
      onConfirm(startTime, endTime)
      setStartTime('')
      setEndTime('')
    }
  }

  const now = new Date()
  const minDateTime = now.toISOString().slice(0, 16)

  return (
    <AlertDialog open={isOpen} onOpenChange={onClose}>
      <AlertDialogContent asChild>
        <motion.div
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.9, opacity: 0 }}
        >
          <AlertDialogHeader>
            <AlertDialogTitle>Reserve Slot #{slotNumber}</AlertDialogTitle>
            <AlertDialogDescription>
              Select your reservation time period. The slot will be held for you during this time.
            </AlertDialogDescription>
          </AlertDialogHeader>
          
          <div className="grid gap-4 py-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="start-time">Start Time</Label>
                <Input
                  id="start-time"
                  type="datetime-local"
                  value={startTime}
                  onChange={(e) => setStartTime(e.target.value)}
                  min={minDateTime}
                />
              </div>
              <div>
                <Label htmlFor="end-time">End Time</Label>
                <Input
                  id="end-time"
                  type="datetime-local"
                  value={endTime}
                  onChange={(e) => setEndTime(e.target.value)}
                  min={startTime || minDateTime}
                />
              </div>
            </div>
          </div>
          
          <AlertDialogFooter>
            <AlertDialogCancel onClick={onClose}>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleConfirm}
              disabled={!startTime || !endTime}
            >
              Reserve Slot
            </AlertDialogAction>
          </AlertDialogFooter>
        </motion.div>
      </AlertDialogContent>
    </AlertDialog>
  )
}