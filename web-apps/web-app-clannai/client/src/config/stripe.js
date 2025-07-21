export const STRIPE_PUBLIC_KEY = process.env.REACT_APP_STRIPE_PUBLIC_KEY;
if (!STRIPE_PUBLIC_KEY) {
    console.error('Missing Stripe public key!');
}

export const stripePromise = loadStripe(STRIPE_PUBLIC_KEY); 