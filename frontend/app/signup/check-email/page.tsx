"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { Suspense, useState } from "react";
import { Button } from "@/components/ui/button";
import { api } from "@/lib/api";

function CheckEmailContent() {
  const searchParams = useSearchParams();
  const email = searchParams.get("email") || "";
  const [resendState, setResendState] = useState<
    "idle" | "sending" | "sent" | "error"
  >("idle");
  const [resendError, setResendError] = useState<string | null>(null);

  const handleResend = async () => {
    if (!email) {
      setResendError("Missing email address — please sign up again.");
      setResendState("error");
      return;
    }
    setResendState("sending");
    setResendError(null);
    try {
      await api.resendConfirmation(email);
      setResendState("sent");
    } catch (err) {
      setResendState("error");
      setResendError(
        err instanceof Error ? err.message : "Failed to resend — try again."
      );
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-50 via-white to-blue-50 px-6 py-12">
      <div className="w-full max-w-md">
        <div className="mb-8 flex justify-center">
          <Link href="/" className="inline-flex items-center gap-2.5">
            <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-primary-500 to-primary-700 flex items-center justify-center">
              <svg
                className="w-5 h-5 text-white"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"
                />
              </svg>
            </div>
            <span className="text-lg font-semibold text-slate-800">
              TravelCompanion
            </span>
          </Link>
        </div>

        <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-8 text-center">
          {/* Envelope icon */}
          <div className="w-16 h-16 mx-auto mb-5 rounded-full bg-primary-50 flex items-center justify-center">
            <svg
              className="w-8 h-8 text-primary-600"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
              />
            </svg>
          </div>

          <h1 className="text-2xl font-bold text-slate-900 mb-3">
            Check your email
          </h1>

          <p className="text-slate-600 mb-2">
            We&apos;ve sent a confirmation link
            {email ? (
              <>
                {" "}
                to <span className="font-medium text-slate-900">{email}</span>
              </>
            ) : null}
            .
          </p>

          <p className="text-sm text-slate-500 mb-6">
            Click the link to activate your account, then come back and sign in.
          </p>

          <div className="border-t border-slate-100 pt-6 space-y-4">
            <p className="text-sm text-slate-500">
              Didn&apos;t receive the email? Check your spam folder, or request
              a new one.
            </p>

            <Button
              onClick={handleResend}
              variant="secondary"
              className="w-full"
              loading={resendState === "sending"}
              disabled={resendState === "sending" || resendState === "sent"}
            >
              {resendState === "sent"
                ? "Confirmation resent"
                : "Resend confirmation email"}
            </Button>

            {resendState === "sent" && (
              <p className="text-sm text-emerald-700 bg-emerald-50 border border-emerald-200 rounded-lg px-3 py-2">
                If an account exists for this email, a new confirmation link
                has been sent.
              </p>
            )}

            {resendState === "error" && resendError && (
              <p className="text-sm text-danger-700 bg-danger-50 border border-danger-200 rounded-lg px-3 py-2">
                {resendError}
              </p>
            )}
          </div>

          <div className="mt-6 pt-6 border-t border-slate-100">
            <Link
              href="/login"
              className="text-sm text-primary-600 font-medium hover:underline"
            >
              Already confirmed? Sign in
            </Link>
          </div>
        </div>

        <p className="text-xs text-slate-400 text-center mt-6">
          Wrong email?{" "}
          <Link href="/signup" className="text-primary-600 hover:underline">
            Sign up again
          </Link>
        </p>
      </div>
    </div>
  );
}

export default function CheckEmailPage() {
  // useSearchParams must live inside a Suspense boundary in Next.js App Router
  // (otherwise the page opts out of static rendering across the whole tree).
  return (
    <Suspense fallback={<div className="min-h-screen" />}>
      <CheckEmailContent />
    </Suspense>
  );
}
